WITH_SELLER = "EPV"
IN_PROGRESS = frozenset(["EPV", "PE"])
UPDATE_PROGRESS = frozenset(["SC", "CF"])
FINAL_STATUS = frozenset(["NR", "SI", "IF", "PR", "VF"])


class DealStatusPolicy:
    """Regras de transição de status de negociação na RD Station."""

    @staticmethod
    def should_update_to_with_seller(deal_status: str) -> bool:
        return deal_status in UPDATE_PROGRESS

    @staticmethod
    def is_in_progress(deal_status: str) -> bool:
        return deal_status in IN_PROGRESS

    @staticmethod
    def is_final(deal_status: str) -> bool:
        return deal_status in FINAL_STATUS

    @staticmethod
    def is_active_in_rd(deal_status: str) -> bool:
        return deal_status in IN_PROGRESS | UPDATE_PROGRESS
