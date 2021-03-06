# Automatically generated by pb2py
# fmt: off
from .. import protobuf as p

from .TezosContractID import TezosContractID

if __debug__:
    try:
        from typing import Dict, List  # noqa: F401
        from typing_extensions import Literal  # noqa: F401
    except ImportError:
        pass


class TezosManagerTransfer(p.MessageType):

    def __init__(
        self,
        *,
        destination: TezosContractID = None,
        amount: int = None,
    ) -> None:
        self.destination = destination
        self.amount = amount

    @classmethod
    def get_fields(cls) -> Dict:
        return {
            1: ('destination', TezosContractID, None),
            2: ('amount', p.UVarintType, None),
        }
