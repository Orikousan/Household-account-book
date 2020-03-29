import unittest
import datetime
import copy
from model.project import project
from model.cashbook import cashbook
from unittest import mock
from decimal import Decimal

# テスト途中で止めたい時は次の行を挿入する
# import pdb; pdb.set_trace()

class test_cashbook(unittest.TestCase):

    def setUp(self):
        # テストで使うcashbookを1つ作成
        # 正しい値を持ったインスタンスを作成しデータベースに登録まで行う
        self.cb = cashbook()
        self.cb.attr["user_id"] = 2
        self.cb.attr["ym"] = 201911
        self.cb.attr["date"] = datetime.datetime.now().date()
        self.cb.attr["summary"] = "バイト賃金"
        self.cb.attr["detail"] = "11月のバイト賃金"
        self.cb.attr["income"] = Decimal(20000)
        self.cb.attr["expenses"] = Decimal(0)
        self.cb.attr["amount"] = Decimal(20000)
        self.cb.attr["last_updated"] = datetime.datetime.now()

        # project.nameを書き換えておくことでテスト用のDBを利用する
        self.patcher = mock.patch('model.project.project.name', return_value="test_cashbook")
        self.mock_name = self.patcher.start()
        cashbook.migrate()
        self.cb.save()

    def tearDown(self):
        # テストが終わるたびにテスト用DBをクリア
        cashbook.db_cleaner()
        self.patcher.stop()
        
    def test_db_is_working(self):
        cb = cashbook.find(self.cb.attr["id"])
        # findで帰ってきているのがidならDBに保存されている
        self.assertTrue(type(cb) is cashbook)
        # 最初のheroなのでidは1になる
        self.assertTrue(cb.attr["id"] == 1)

    # attrが正しい値を持っている
    def test_is_valid(self):
        self.assertTrue(self.cb.is_valid())

    # attrが間違った値を持っているかをチェックする関数のテスト
    def test_is_valid_with_invalid_attrs(self):
        cb_wrong = copy.deepcopy(self.cb)
        cb_wrong.attr["id"] = None # id must be None or a int
        self.assertTrue(cb_wrong.is_valid())
        cb_wrong = copy.deepcopy(self.cb)
        cb_wrong.attr["id"] = "1" # id must be None or a int
        self.assertFalse(cb_wrong.is_valid())
        cb_wrong = copy.deepcopy(self.cb)
        cb_wrong.attr["user_id"] = None # user_id must be a int
        self.assertFalse(cb_wrong.is_valid())
        cb_wrong = copy.deepcopy(self.cb)
        cb_wrong.attr["ym"] = 1911 # ym must be a int and its length must be 6
        self.assertFalse(cb_wrong.is_valid())
        cb_wrong = copy.deepcopy(self.cb)
        cb_wrong.attr["date"] = 12345 # date must be a datatime.date object
        self.assertFalse(cb_wrong.is_valid())
        cb_wrong = copy.deepcopy(self.cb)
        cb_wrong.attr["summary"] = 12345 # summary must be a sting
        self.assertFalse(cb_wrong.is_valid())
        cb_wrong = copy.deepcopy(self.cb)
        cb_wrong.attr["detail"] = None # detail must be None or a string
        self.assertTrue(cb_wrong.is_valid())
        cb_wrong = copy.deepcopy(self.cb)
        cb_wrong.attr["detail"] = 12345 # detail must be None or a string
        self.assertFalse(cb_wrong.is_valid())
        cb_wrong = copy.deepcopy(self.cb)
        cb_wrong.attr["income"] = 12345 # income must be a Desimal
        self.assertFalse(cb_wrong.is_valid())
        cb_wrong = copy.deepcopy(self.cb)
        cb_wrong.attr["expenses"] = 12345 # expansed must be a Desimal
        self.assertFalse(cb_wrong.is_valid())
        cb_wrong = copy.deepcopy(self.cb)
        cb_wrong.attr["amount"] = Decimal(-20000) #amount must be equal to income + expamses
        self.assertFalse(cb_wrong.is_valid())
        cb_wrong = copy.deepcopy(self.cb)
        cb_wrong.attr["last_updated"] = None # last_updated must be a datetime.datetime object
        self.assertFalse(cb_wrong.is_valid())

    # default値を持ったcashbookインスタンスを生成する
    # Controlerで入力フォームを作るのにも利用する
    def test_build(self):
        cb = cashbook.build()
        self.assertTrue(type(cb) is cashbook)

    # save関数のテストを行う
    # 正例だけ出なく負例もテストするとなお良い
    def test_save(self):
        cb = cashbook.build()
        cb.attr["user_id"] = 2
        cb.attr["summary"] = "テスト"
        cb.attr["detail"] = None
        cb.attr["income"] += 10000
        cb.attr["expenses"] += 5000
        cb.attr["amount"] += 5000
        cb_id = cb.save()
        #import pdb; pdb.set_trace()
        self.assertTrue(type(cb_id) is int)
        self.assertTrue(cb.attr["id"] is not None)
        self.assertTrue(cb_id == cb.attr["id"])
        self.assertTrue(cb_id == 2)

    def test__index(self):
        self.assertEqual(len(cashbook._index(2)), 1)
        self.assertEqual(cashbook._index(2)[0], 1)

    def test_summary(self):
        user_id = 2
        summary = '光熱費'
        cb1 = cashbook.build()
        cb2 = cashbook.build()

        cb1.attr["user_id"] = user_id
        cb1.attr["date"] = '2019-11-30'
        cb1.attr["summary"] = summary
        cb1.attr["detail"] = None
        cb1.attr["income"] += 0
        cb1.attr["expenses"] += 5000
        cb1.attr["amount"] += -5000
        cb1_id = cb1.save()

        cb2.attr["user_id"] = user_id
        cb2.attr["date"] = '2019-12-30'
        cb2.attr["summary"] = summary
        cb2.attr["detail"] = None
        cb2.attr["income"] += 0
        cb2.attr["expenses"] += 7000
        cb2.attr["amount"] += -7000
        cb2_id = cb2.save()

        cb_list = cashbook.find_summary(user_id, summary)
        self.assertEqual(len(cb_list), 2)
        self.assertTrue(type(cb_list[0]) is cashbook)
        self.assertTrue(cb_list[0].attr['date'] < cb_list[1].attr['date'])

    def test_datetime(self):
        user_id = 3
        ym = '201911'
        cb1 = cashbook.build()
        cb2 = cashbook.build()

        cb1.attr["user_id"] = user_id
        cb1.attr["date"] = datetime.date(2019, 11, 18)
        cb1.attr["ym"] = cb1.attr["date"].year * 100 + cb1.attr["date"].month
        cb1.attr["summary"] = '交通費'
        cb1.attr["detail"] = None
        cb1.attr["income"] += 0
        cb1.attr["expenses"] += 5000
        cb1.attr["amount"] += -5000
        cb1_id = cb1.save()

        cb2.attr["user_id"] = user_id
        cb2.attr["date"] = datetime.date(2019, 11, 2)
        cb2.attr["ym"] = cb2.attr["date"].year * 100 + cb2.attr["date"].month
        cb2.attr["summary"] = '光熱費'
        cb2.attr["detail"] = None
        cb2.attr["income"] += 0
        cb2.attr["expenses"] += 7000
        cb2.attr["amount"] += -7000
        cb2_id = cb2.save()

        cb_list = cashbook.find_datetime(user_id, ym)
        self.assertEqual(len(cb_list), 2)
        self.assertTrue(type(cb_list[0]) is cashbook)
        self.assertTrue(cb_list[0].attr['ym'] == cb_list[1].attr['ym'])
        self.assertTrue(cb_list[0].attr['date'] < cb_list[1].attr['date'])

if __name__ == '__main__':
    # unittestを実行
    unittest.main()