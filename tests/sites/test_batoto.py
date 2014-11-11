from unittest import TestCase, main
from pytaku.sites import Batoto

site = Batoto()


class SeriesInfo(TestCase):

    def test_normal(self):
        url = 'http://bato.to/comic/_/comics/death-note-fatestay-night-death-fate-doujinshi-r8315'
        info = site.series_info(site.fetch_manga_seed_page(url))
        self.assertIsInstance(info, dict)

        # Attributes that can be asserted by exact value:
        expected = {
            'name': 'Death Note & Fate/stay night - DEATH FATE (Doujinshi)',
            'site': 'batoto',
            'thumb_url': 'http://img.batoto.net/forums/uploads/0df871710e288e88fbd82f67e0486e6a.png',
            'tags': ['comedy', 'doujinshi', 'supernatural', 'tragedy'],
            'authors': ['Makegumi Club (Circle)', 'Matsuri', 'Wasu', 'Zephyr'],
            'status': 'complete',
        }
        for key, val in expected.iteritems():
            print '>>> Asserting', key
            print '>>>>>>', info[key]
            print '======================='
            self.assertEqual(info[key], val)

        # The rest:

        self.assertIsInstance(info['description'], list)
        for d in info['description']:
            self.assertIsInstance(d, unicode)

        self.assertIsInstance(info['status'], unicode)

        chapters = info['chapters']
        self.assertIsInstance(chapters, list)
        self.assertTrue(len(chapters) == 2)
        for chap in chapters:
            self.assertIsInstance(chap, dict)
            self.assertIn('url', chap)
            self.assertIn('name', chap)


if __name__ == '__main__':
    main()
