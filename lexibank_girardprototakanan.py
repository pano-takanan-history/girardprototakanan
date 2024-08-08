import attr
import pathlib
from collections import defaultdict
from clldutils.misc import slug
from lingpy import Wordlist
from pylexibank import Dataset as BaseDataset
from pylexibank import progressbar as pb
from pylexibank import Language, Lexeme, Concept
from pylexibank import FormSpec
from pyedictor import fetch


def unmerge(sequence):
    out = []
    for tok in sequence:
        out += tok.split('.')
    return out

@attr.s
class CustomLanguage(Language):
    NameInSource = attr.ib(default=None)


@attr.s
class CustomConcept(Concept):
    Proto_ID = attr.ib(default=None)
    Original_Concept = attr.ib(default=None)


@attr.s
class CustomLexeme(Lexeme):
    Alignment = attr.ib(default=None)
    ProtoSet = attr.ib(default=None)
    ConceptInSource = attr.ib(default=None)
    GroupedSounds = attr.ib(default=None)


class Dataset(BaseDataset):
    dir = pathlib.Path(__file__).parent
    id = "girardprototakanan"
    language_class = CustomLanguage
    concept_class = CustomConcept
    lexeme_class = CustomLexeme
    writer_options = dict(keep_languages=False, keep_parameters=False)
    form_spec = FormSpec(
        separators="~;,",
        missing_data=["--", "- -", "-", "-- **", "--.", "- --"],
        replacements=[
            (" ", "_"),
            ("<-zu>", "-zu"),
            ("<tawa-daʔa>", "tawa-daʔa"),
            ("<{s/z}awa-da>", "Sawa-da"),
            ("{u/o}", "U"),
            ("{e/ä}", "E"),
            ("{a/e}", "A"),
            ("{i/e}", "I"),
            ("{e/i}", "I"),
            ("{a/u}", "Ä")
        ],
        first_form_only=True
        )

    def cmd_download(self, _):
        print("updating...")
        with open(self.raw_dir.joinpath("data.tsv"), "w", encoding="utf-8") as f:
            f.write(
                fetch(
                    "girardprototakanan",
                    columns=[
                        "ALIGNMENT",
                        "COGID",
                        "CONCEPT",
                        "DOCULECT",
                        "FORM",
                        "VALUE",
                        "TOKENS",
                        "NOTE",
                        "SOURCE",
                        "PROTOSET",
                        "CONCEPTINSOURCE",
                    ],
                    base_url="http://lingulist.de/edev"
                )
            )

    def cmd_makecldf(self, args):
        args.writer.add_sources()
        args.log.info("added sources")

        # add conceptlists
        concepts = defaultdict()

        # Proto Concepts: New
        proto_list = self.etc_dir.read_csv(
            "proto_concepts.tsv",
            delimiter="\t",
            dicts=True
            )

        for concept in proto_list:
            idx = slug(concept["PROTO_CONCEPT"])
            args.writer.add_concept(
                ID=idx,
                Name=concept["PROTO_CONCEPT"],
                Original_Concept=concept["SPANISH"],
                Concepticon_ID=concept["CONCEPTICON_ID"],
                Concepticon_Gloss=concept["CONCEPTICON_GLOSS"],
                Proto_ID=concept["PROTO_ID"]
                )

            concepts[concept["PROTO_CONCEPT"]] = idx

        # Other Concepts
        other_concepts = self.etc_dir.read_csv(
            "other_concepts.tsv",
            delimiter="\t",
            dicts=True
            )

        for concept in other_concepts:
            idx = slug(concept["PROTO_CONCEPT"])
            args.writer.add_concept(
                ID=idx,
                Name=concept["PROTO_CONCEPT"],
                Original_Concept=concept["GLOSS"],
                Proto_ID=concept["PROTO_ID"],
                )
            concepts[concept["PROTO_CONCEPT"]] = idx

        args.log.info("added concepts")

        # add language
        languages = args.writer.add_languages(lookup_factory="ID")
        args.log.info("added languages")

        data = Wordlist(str(self.raw_dir.joinpath("data.tsv")))

        # add data
        for (
            idx,
            alignment,
            cogid,
            concept,
            doculect,
            form,
            value,
            tokens,
            note,
            source,
            protoset,
            conceptinsource
        ) in pb(
            data.iter_rows(
                "alignment",
                "cogid",
                "concept",
                "doculect",
                "form",
                "value",
                "tokens",
                "note",
                "source",
                "protoset",
                "conceptinsource"
            ),
            desc="cldfify"
        ):
            lexeme = args.writer.add_form_with_segments(
                Language_ID=languages[doculect],
                Parameter_ID=concepts[(concept)],
                Value=value.strip() or form.strip(),
                Form=form.strip(),
                Segments=unmerge(tokens),
                GroupedSounds=tokens,
                Comment=note,
                Source=source.split(" "),
                ProtoSet=protoset,
                Cognacy=cogid,
                Alignment=" ".join(alignment),
                ConceptInSource=conceptinsource,
            )

            args.writer.add_cognate(
                lexeme=lexeme,
                Cognateset_ID=cogid,
                Cognate_Detection_Method="expert",
                Source="Girard1971"
            )
