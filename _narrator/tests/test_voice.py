"""Stage 3 — text chunking, silence trimming, keys, chapters. No network, no ffmpeg."""
import array
import os
import tempfile
import unittest

from _narrator import script as stage2
from _narrator import voice
from _narrator.prompts import PROMPT_VERSION
from _narrator.tests.test_script import skel


class ScriptsFor(unittest.TestCase):
    """Which scripts a page may be built from — the gate `publish` uses before speaking."""

    def write(self, root, prompt, edit=False):
        s = skel()
        directory = stage2.post_dir(root, s)
        for section in s.sections:
            if section.skip:
                continue
            body = "A clean script."
            stage2.write_md(os.path.join(directory, section.id + ".md"), {
                "section": section.id, "source": section.hash, "prompt": prompt,
                "body": stage2._sha(body)}, body + (" Edited by hand." if edit else ""))
        return s

    def test_scripts_from_the_current_prompt_are_used(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(len(voice.scripts_for(self.write(tmp, PROMPT_VERSION), tmp)), 2)

    def test_scripts_from_an_older_prompt_are_out_of_date(self):
        with tempfile.TemporaryDirectory() as tmp:
            s = self.write(tmp, "lecture-v0")
            with self.assertRaisesRegex(voice.VoiceError, "scripts out of date: introduction, theorem-1"):
                voice.scripts_for(s, tmp)

    def test_a_hand_edited_script_outlives_a_prompt_bump(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(len(voice.scripts_for(self.write(tmp, "lecture-v0", edit=True), tmp)), 2)


class Text(unittest.TestCase):
    def test_spoken_labels(self):
        self.assertEqual(voice.spoken_labels("By Theorem 2.1.18 and Definition 2.2.1."),
                         "By Theorem 2 point 1 point 18 and Definition 2 point 2 point 1.")
        self.assertEqual(voice.spoken_labels("about 2.5 units and Theorem 3."), "about 2.5 units and Theorem 3.")
        self.assertEqual(voice.spoken_labels("1.1.1 Traders.\n\nTraders hold 2.5 units."),
                         "1 point 1 point 1 Traders.\n\nTraders hold 2.5 units.")

    def test_chunks_paragraphs(self):
        out = voice.chunks("One.\n\nTwo.\n  \nThree.\n")
        self.assertEqual(out, [("One.", 0.0), ("Two.", voice.PARA_GAP), ("Three.", voice.PARA_GAP)])

    def test_chunks_split_long_paragraph_at_sentences(self):
        sentence = "This is a sentence that goes on for a while. "
        para = sentence * 120                      # ~5400 chars
        out = voice.chunks(para)
        self.assertGreater(len(out), 1)
        for text, _gap in out:
            self.assertLessEqual(len(text), voice.MAX_CHARS)
            self.assertTrue(text.endswith("."))
        self.assertEqual(out[0][1], 0.0)
        self.assertEqual(out[1][1], voice.SENTENCE_GAP)
        self.assertEqual(" ".join(t for t, _ in out), para.strip())

    def test_section_key_depends_on_voice_and_text_only_canonically(self):
        a = voice.section_key("Hello.\n\nWorld.  \n", "cedar", "gpt-4o-mini-tts")
        b = voice.section_key("\nHello.\n\nWorld.\n\n", "cedar", "gpt-4o-mini-tts")
        c = voice.section_key("Hello.\n\nWorld.", "onyx", "gpt-4o-mini-tts")
        d = voice.section_key("Hello.\n\nWorlds.", "cedar", "gpt-4o-mini-tts")
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)
        self.assertNotEqual(a, d)


class Pcm(unittest.TestCase):
    def test_trim_keeps_a_little_silence(self):
        sr = voice.SR
        quiet = array.array("h", [0] * sr)                 # 1 s
        loud = array.array("h", [10000] * (sr // 2))       # 0.5 s
        pcm = (quiet + loud + quiet).tobytes()
        out = voice.trim(pcm)
        expect = 0.5 + 2 * voice.TRIM_KEEP
        self.assertAlmostEqual(voice.seconds(out), expect, places=3)

    def test_silence_length(self):
        self.assertEqual(len(voice.silence(1.2)), int(1.2 * voice.SR) * voice.BPS)


class Metadata(unittest.TestCase):
    def test_ffmetadata_escapes(self):
        text = voice.ffmetadata("a=b; c", "Me", "Al", [{"title": "One #1", "start": 0, "end": 1.5}])
        self.assertIn("title=a\\=b\; c", text)
        self.assertIn("[CHAPTER]\nTIMEBASE=1/1000\nSTART=0\nEND=1500\ntitle=One \\#1", text)




class Concurrency(unittest.TestCase):
    def test_same_key_is_synthesised_once(self):
        import os, tempfile, threading, json
        from concurrent.futures import ThreadPoolExecutor
        calls = []
        lock = threading.Lock()

        def fake_synth(text, voice, model, instructions="", timeout=0):
            with lock:
                calls.append(text)
            import time; time.sleep(0.05)
            return b"\x00\x10" * voice_mod.SR       # one second of faint noise

        def fake_flac(pcm, path):
            with open(path, "wb") as f:
                f.write(pcm)

        voice_mod = voice
        real_synth, real_flac = voice_mod.tts.synth, voice_mod.encode_flac
        voice_mod.tts.synth, voice_mod.encode_flac = fake_synth, fake_flac
        try:
            with tempfile.TemporaryDirectory() as tmp:
                with ThreadPoolExecutor(max_workers=4) as pool:
                    metas = list(pool.map(lambda _i: voice_mod.ensure_section(tmp, "s", "Hello there.", "cedar", "m", log=lambda m: None), range(4)))
                self.assertEqual(len(calls), 1)
                self.assertEqual(len({m["key"] for m in metas}), 1)
                self.assertTrue(os.path.exists(os.path.join(tmp, metas[0]["key"] + ".json")))
                self.assertEqual(json.load(open(os.path.join(tmp, metas[0]["key"] + ".json")))["chars"], len("Hello there."))
        finally:
            voice_mod.tts.synth, voice_mod.encode_flac = real_synth, real_flac


if __name__ == "__main__":
    unittest.main()
