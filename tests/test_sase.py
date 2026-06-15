import unittest
from core.sase import SASE
from core.types import SEA, SEAStatus, SEATipo
from impl.memory_dao import InMemoryDAO


def build_sase() -> SASE:
    return SASE(InMemoryDAO())


class TestSase(unittest.TestCase):
    def test_sea_is_created(self):
        sase = build_sase()

        sea = sase.gerar_sea("normal")
        self.assertIsInstance(sea, SEA)
        self.assertEqual(sea.tipo, SEATipo.NORMAL)
        self.assertEqual(sea.status, SEAStatus.CRIADA)

    def test_sea_generated_value_is_sequential(self):
        sase = build_sase()

        sea1 = sase.gerar_sea("normal")
        sea2 = sase.gerar_sea("normal")

        self.assertEqual(sea1.senha, "N1")
        self.assertEqual(sea2.senha, "N2")

    def test_sea_generated_value_is_sequential_per_type(self):
        sase = build_sase()

        normal1 = sase.gerar_sea("normal")
        normal2 = sase.gerar_sea("normal")
        prioritaria1 = sase.gerar_sea("prioritaria")
        normal3 = sase.gerar_sea("normal")
        prioritaria2 = sase.gerar_sea("prioritaria")

        self.assertEqual(normal1.senha, "N1")
        self.assertEqual(normal2.senha, "N2")
        self.assertEqual(prioritaria1.senha, "P1")
        self.assertEqual(normal3.senha, "N3")
        self.assertEqual(prioritaria2.senha, "P2")

    def test_sea_type_is_validated(self):
        sase = build_sase()

        sase.gerar_sea("normal")
        sase.gerar_sea("prioritaria")

        with self.assertRaises(Exception):
            sase.gerar_sea("invalido")

    def test_sea_can_be_marked_as_called(self):
        sase = build_sase()

        sea = sase.chamar_senha()
        self.assertIsNone(sea)

        sase.gerar_sea("normal")

        sea = sase.chamar_senha()
        self.assertIsInstance(sea, SEA)
        self.assertEqual(sea.status, SEAStatus.CHAMADA)

    def test_every_two_called_seas_one_is_prioritary(self):
        sase = build_sase()

        sase.gerar_sea("normal")
        sase.gerar_sea("normal")
        sase.gerar_sea("normal")
        sase.gerar_sea("prioritaria")

        sea = sase.chamar_senha()
        self.assertEqual(sea.tipo, SEATipo.NORMAL)

        sea = sase.chamar_senha()
        self.assertEqual(sea.tipo, SEATipo.NORMAL)

        sea = sase.chamar_senha()
        self.assertEqual(sea.tipo, SEATipo.PRIORITARIA)

    def test_sea_is_not_called_twice(self):
        sase = build_sase()

        sase.gerar_sea("normal")
        sase.chamar_senha()

        sea = sase.chamar_senha()
        self.assertIsNone(sea)
