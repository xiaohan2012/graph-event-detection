import unittest
from .enron_util import truncate_message


class TruncateMessageTest(unittest.TestCase):
    def run_template(self, useful, junk):
        
        msg = '{}{}'.format(
            useful, junk
            
        )
        self.assertEqual(
            useful,
            truncate_message(msg)
        )

    def test_truncate_message_1(self):
        self.run_template(
            'His extension is 3-5612. Vince    ',
            '-----Original Message----- From: \\'
        )

    def test_truncate_message_2(self):
        self.run_template(
            'I  already complied? ',
            '---------------------- Forwarded by Steven J Kean/NA/Enron on 07/11/2001  01:19 PM ---------------------------  '
        )

    def test_truncate_message_3(self):
        self.run_template(
            'His extension is 3-5612. Vince    ',
            '-----original message----- From: \\'
        )

    def test_truncate_message_4(self):
        self.run_template(
            'His extension is 3-5612. Vince    ----nice',
            ''
        )

    def test_truncate_message_5(self):
        self.run_template(
            'when we merged in 1997. ',
            '---------------------- Forwarded by Steven'
        )

    def test_truncate_message_6(self):
        self.run_template(
            'Best, Jeff ',
            '********************************************************************** Financial  California'
        )
        
