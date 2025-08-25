from abc import ABC, abstractmethod


class OtpSender(ABC):
    @abstractmethod
    def send(self, to: str, message: str) -> None:
        pass

class ConsoleSender(OtpSender):
    """Dev sender: prints to console/log; replace with manipal service later."""
    def send(self, to: str, message: str) -> None:
        print(f"[DEV-OTP] to={to} msg={message}")

