#!/usr/bin/env python3
"""Contrôle local des liens MP4 de la galerie et de l'intégrité d'un téléchargement."""
import hashlib
import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import serveur

class TestTelechargements(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.server=ThreadingHTTPServer(('127.0.0.1',0),serveur.Handler)
  cls.root=f'http://127.0.0.1:{cls.server.server_port}'
  cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
  cls.data=serveur.catalogue()
 @classmethod
 def tearDownClass(cls):
  cls.server.shutdown();cls.server.server_close();cls.thread.join()
 def test_tous_les_liens_de_telechargement(self):
  for item in self.data['videos']:
   with self.subTest(id=item['id']):
    req=Request(self.root+'/telecharger/'+item['id']+'.mp4',method='HEAD')
    with urlopen(req,timeout=10) as r:
     self.assertEqual(r.status,200);self.assertEqual(r.headers.get_content_type(),'video/mp4')
     self.assertTrue(r.headers.get('Content-Disposition','').startswith('attachment;'))
     self.assertEqual(int(r.headers['Content-Length']),Path(item['path']).stat().st_size)
 def test_telechargement_identique(self):
  item=next(x for x in self.data['videos'] if x['id']=='armor_cannon_base_v2_corrige')
  with urlopen(self.root+'/telecharger/'+item['id']+'.mp4',timeout=30) as r:
   downloaded=hashlib.sha256(r.read()).hexdigest()
  self.assertEqual(downloaded,hashlib.sha256(Path(item['path']).read_bytes()).hexdigest())
 def test_lecture_partielle_et_fichier_inconnu(self):
  item=self.data['videos'][0]
  with urlopen(Request(self.root+'/media/'+item['id'],headers={'Range':'bytes=0-1023'}),timeout=10) as r:
   self.assertEqual(r.status,206);self.assertEqual(len(r.read()),1024)
  with self.assertRaises(HTTPError) as error:urlopen(self.root+'/telecharger/inconnu.mp4',timeout=10)
  self.assertEqual(error.exception.code,404)

if __name__=='__main__':unittest.main(verbosity=2)
