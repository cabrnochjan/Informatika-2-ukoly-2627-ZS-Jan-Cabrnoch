import argparse
import functools
import re
from abc import ABC, abstractmethod
from typing import Any, Callable


class NeplatnyKodZasilkyError(Exception):
    pass


def over_kod_zasilky(kod: str) -> dict[str, str]:
    vzor = r"^([A-Z]{2})-(\d{6})-([A-Z]{3})$"
    m = re.match(vzor, kod)

    if m:
        return {"zeme": m.group(1), "cislo": m.group(2), "typ": m.group(3)}
    else:
        raise NeplatnyKodZasilkyError("Neplatný formát kódu zásilky.")


def over_kladne_argumenty(func: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        hodnoty = list(args) + list(kwargs.values())

        for x in hodnoty:
            if type(x) in (int, float):
                if x <= 0:
                    raise ValueError("Číselný argument musí být kladný.")

        vysledek = func(*args, **kwargs)

        return vysledek

    return wrapper


class Zasilka(ABC):
    def __init__(self, kod: str, hmotnost_kg: float) -> None:
        if kod.strip() != "":
            self.kod = kod.strip()
        else:
            raise ValueError("Kód zásilky nesmí být prázdný.")

        if hmotnost_kg > 0:
            self.hmotnost_kg = float(hmotnost_kg)
        else:
            raise ValueError("Hmotnost musí být kladná.")

    @abstractmethod
    def spocitej_cenu(self) -> float:
        pass

    def __str__(self) -> str:
        return f"Zásilka {self.kod} [{self.spocitej_cenu():.2f} Kč]"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(kod='{self.kod}', hmotnost_kg={self.hmotnost_kg})"

    def __eq__(self, other: object) -> bool:
        if (self.__class__ == other.__class__) and (self.kod == other.kod):
            return True
        else:
            return False

    def __lt__(self, other: object) -> bool:
        if isinstance(other, Zasilka):
            return self.spocitej_cenu() < other.spocitej_cenu()
        else:
            return NotImplemented

    def __add__(self, other: object) -> float:
        if isinstance(other, Zasilka):
            return self.spocitej_cenu() + other.spocitej_cenu()
        else:
            return NotImplemented


class StandardniZasilka(Zasilka):
    def __init__(self, kod: str, hmotnost_kg: float) -> None:
        super().__init__(kod, hmotnost_kg)

    def spocitej_cenu(self) -> float:
        return round(60.0 + self.hmotnost_kg * 15.0, 2)


class ExpresniZasilka(Zasilka):
    def __init__(self, kod: str, hmotnost_kg: float, priplatek: float = 100.0) -> None:
        super().__init__(kod, hmotnost_kg)
        if priplatek >= 0:
            self.priplatek = float(priplatek)
        else:
            raise ValueError("Příplatek nesmí být záporný.")

    def spocitej_cenu(self) -> float:
        return round((60.0 + self.hmotnost_kg * 25.0) + self.priplatek, 2)


def vytvor_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("kod", type=str, help="Kód zásilky")
    parser.add_argument("hmotnost", type=float, help="Hmotnost zásilky v kg")
    parser.add_argument("--typ", "-t", type=str, choices=["standard", "expres"], default="standard", help="Typ zásilky")
    parser.add_argument("--priplatek", "-p", type=float, default=100.0, help="Expresní příplatek")

    return parser


def vytvor_zasilku_z_argumentu(args: argparse.Namespace) -> Zasilka:
    if args.typ == "standard":
        return StandardniZasilka(args.kod, args.hmotnost)
    else:
        return ExpresniZasilka(args.kod, args.hmotnost, priplatek=args.priplatek)


if __name__ == "__main__":
    parser = vytvor_parser()
    args = parser.parse_args()

    try:
        print(vytvor_zasilku_z_argumentu(args))
    except NeplatnyKodZasilkyError as e:
        print(f"Neplatny kod, err: {e}")
    except ValueError as e:
        print(f"Chybna hodnota, err: {e}")