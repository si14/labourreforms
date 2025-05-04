from datetime import datetime
from enum import Enum
from typing import Optional

import humanize
from pydantic import BaseModel

from data_pull import Group, read_bills


class HouseEnum(Enum):
    COMMONS = "Commons"
    LORDS = "Lords"
    UNASSIGNED = "Unassigned"


class StageSittings(BaseModel):
    date: datetime


class BillCurrentStage(BaseModel):
    abbreviation: str
    description: str
    house: HouseEnum
    sortOrder: int
    stageSittings: list[StageSittings]


class BillDetails(BaseModel):
    originatingHouse: HouseEnum
    currentHouse: HouseEnum
    currentStage: BillCurrentStage
    formerShortTitle: Optional[str] = None
    isAct: bool
    isDefeated: bool
    lastUpdate: datetime
    longTitle: str
    originatingHouse: HouseEnum
    shortTitle: str
    summary: Optional[str] = None


class Descriptions(BaseModel):
    theguardian: Optional[str] = None
    ft: Optional[str] = None
    parliament: Optional[str] = None


class Stage(Enum):
    LORDS = "Lords"
    COMMONS = "Commons"
    FINAL = "Assent"


class State(Enum):
    PASSED = "passed"
    PASSING = "passing"
    FUTURE = "future"


class StageState(BaseModel):
    stage: Stage
    state: State


class Progress(BaseModel):
    stages: list[StageState]
    last_update: str


class Enacted(BaseModel):
    enacted_for: str


class ProcessedBill(BaseModel):
    group: Group
    title: str
    descriptions: Descriptions
    display_stage: Optional[str]

    progress: Optional[Progress] = None
    enacted: Optional[Enacted] = None

    parliament_id: Optional[int] = None
    context_url: Optional[str] = None


class Stats(BaseModel):
    total: int
    lords: int
    commons: int
    final: int
    enacted: int


class Result(BaseModel):
    last_update: str
    stats: Stats
    bills: list[ProcessedBill]


def guess_bill_state(bill: BillDetails) -> tuple[Optional[Progress], Optional[Enacted]]:
    if bill.isAct:
        assert bill.currentStage.abbreviation == "RA"
        assert len(bill.currentStage.stageSittings) == 1
        enacted_at = bill.currentStage.stageSittings[0].date
        enacted_for = humanize.naturaldelta(datetime.now() - enacted_at)
        return None, Enacted(enacted_for=enacted_for)

    if bill.originatingHouse is HouseEnum.COMMONS:
        stage_order = [Stage.COMMONS, Stage.LORDS, Stage.FINAL]
    else:
        stage_order = [Stage.LORDS, Stage.COMMONS, Stage.FINAL]

    stages = [StageState(stage=s, state=State.FUTURE) for s in stage_order]

    current_stage = {
        HouseEnum.COMMONS: Stage.COMMONS,
        HouseEnum.LORDS: Stage.LORDS,
        HouseEnum.UNASSIGNED: Stage.FINAL,
    }[bill.currentStage.house]

    for i in range(len(stages)):
        stages[i].state = State.PASSED

        if stages[i].stage == current_stage:
            stages[i].state = State.PASSING
            break

    return Progress(
        stages=stages, last_update=bill.lastUpdate.strftime("%d %B %Y")
    ), None


def count_bills_at(bills: list[ProcessedBill], stage: Stage) -> int:
    return sum(
        1
        for b in bills
        if b.progress is not None
        and any(
            s == StageState(stage=stage, state=State.PASSING) for s in b.progress.stages
        )
    )


def main():
    groups, bills = read_bills()

    processed_bills = []

    for bill in bills:
        if bill.parliament_id is None:
            processed_bills.append(
                ProcessedBill(
                    group=groups[bill.group],
                    title=bill.title,
                    context_url=bill.context_url,
                    descriptions=Descriptions(
                        theguardian=bill.theguardian,
                        ft=bill.ft,
                    ),
                    display_stage=None,
                )
            )
            continue

        with open(f"data_cache/bill_{bill.parliament_id}.json") as f:
            bill_details = BillDetails.model_validate_json(f.read())

        assert bill.context_url is None

        progress, enacted = guess_bill_state(bill_details)

        display_stage: Stage
        if enacted is not None:
            display_stage = Stage.FINAL
        else:
            display_stage = [
                stage for stage in progress.stages if stage.state == State.PASSING
            ][0].stage

        processed_bills.append(
            ProcessedBill(
                group=groups[bill.group],
                title=bill.title,
                parliament_id=bill.parliament_id,
                context_url=None,
                descriptions=Descriptions(
                    theguardian=bill.theguardian,
                    ft=bill.ft,
                    parliament=f"<p>{bill_details.longTitle}</p>",
                ),
                display_stage={
                    Stage.COMMONS: "commons",
                    Stage.LORDS: "lords",
                    Stage.FINAL: "final",
                }[display_stage],
                progress=progress,
                enacted=enacted,
            )
        )

    stats = Stats(
        total=len(processed_bills),
        lords=count_bills_at(processed_bills, Stage.LORDS),
        commons=count_bills_at(processed_bills, Stage.COMMONS),
        final=count_bills_at(processed_bills, Stage.FINAL),
        enacted=sum(1 for b in processed_bills if b.enacted is not None),
    )

    result = Result(
        last_update=datetime.now().strftime("%d %B %Y"),
        bills=processed_bills,
        stats=stats,
    )

    with open("data.json", "w") as f:
        f.write(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
