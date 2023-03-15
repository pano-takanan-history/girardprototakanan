import attr
import pathlib
from collections import defaultdict
from clldutils.misc import slug
from lingpy import Wordlist
from pylexibank import Dataset as BaseDataset
from pylexibank import progressbar as pb
from pylexibank import Language, Lexeme, Concept
from pylexibank import FormSpec


@attr.s
class CustomLanguage(Language):
    NameInSource = attr.ib(default=None)
#    Sources = attr.ib(default=None)


@attr.s
class CustomConcept(Concept):
    Proto_Concept = attr.ib(default=None)
    Proto_ID = attr.ib(default=None)
    Original_Concept = attr.ib(default=None)


@attr.s
class CustomLexeme(Lexeme):
    UncertainCognacy = attr.ib(default=None)
    Concept_From_Proto = attr.ib(default=None)
    ProtoSet = attr.ib(default=None)
    EntryInSource = attr.ib(default=None)
    Variants = attr.ib(default=None)
    ConceptInSource = attr.ib(default=None)


class Dataset(BaseDataset):
    dir = pathlib.Path(__file__).parent
    id = "girardprototakanan"
    language_class = CustomLanguage
    concept_class = CustomConcept
    lexeme_class = CustomLexeme
    form_spec = FormSpec(
            separators="~;,/",
            missing_data=["--", "- -", "-", "-- **", "--.", "- --"],
            replacements=[(" ", "_")],
            first_form_only=True
            )

    def cmd_makecldf(self, args):
        args.writer.add_sources()
        args.log.info("added sources")

        # add conceptlists
        concepts = defaultdict()
        proto_concepts = defaultdict()

        # Proto Concepts: New
        proto_list = self.etc_dir.read_csv(
            "proto_concepts.tsv",
            delimiter="\t",
            dicts=True
            )

        for concept in proto_list:
            idx = slug(concept["GLOSS"])
            args.writer.add_concept(
                ID=idx,
                Name=concept["PROTO_CONCEPT"],
                Original_Concept=concept["GLOSS"],
                Concepticon_ID=concept["CONCEPTICON_ID"],
                Concepticon_Gloss=concept["CONCEPTICON_GLOSS"],
                Proto_ID=concept["PROTO_ID"]
                )

            concepts[concept["GLOSS"]] = idx

        # Other Concepts
        other_concepts = self.etc_dir.read_csv(
            "other_concepts.tsv",
            delimiter="\t",
            dicts=True
            )

        for concept in other_concepts:
            idx = slug(concept["GLOSS"])
            args.writer.add_concept(
                ID=idx,
                Name=concept["PROTO_CONCEPT"],
                Original_Concept=concept["GLOSS"],
                Proto_ID=concept["PROTO_ID"],
                )
            concepts[concept["GLOSS"]] = idx

        args.log.info("added concepts")

        # add language
        languages = args.writer.add_languages(lookup_factory="ID")
        args.log.info("added languages")

        data = Wordlist(str(self.raw_dir.joinpath("data.tsv")))
        data.renumber("PROTO_SET", "cogid")

        # add data
        for (
            idx,
            proto_set,
            proto_entry,
            proto_form,
            proto_concept,
            doculect,
            concept,
            value,
            morph_infor,
            note,
            uncertainty,
            cogid
        ) in pb(
            data.iter_rows(
                "proto_set",
                "proto_entry",
                "proto_form",
                "proto_concept",
                "doculect",
                "concept",
                "value",
                "morph_infor",
                "note",
                "uncertainty",
                "cogid"
            ),
            desc="cldfify"
        ):
            if " [" in value:
                phon = value.split(" [")[1:]
                value = phon[0].strip("] ~")
                variants = (str(phon[1]).strip("] ~") if len(phon) > 1 else "")

            else:
                variants = ""

            for lexeme in args.writer.add_forms_from_value(
                    Language_ID=languages[doculect],
                    Parameter_ID=concepts[(concept)],
                    Value=value,
                    #Entry_From_Proto=proto_entry,
                    #Form_From_Proto=proto_form,
                    #Morphological_Information=morph_infor,
                    Concept_From_Proto=proto_concept,
                    Variants=variants,
                    Comment=note,
                    #Source=source,
                    UncertainCognacy=uncertainty,
                    ProtoSet=proto_set,
                    Cognacy=cogid,
                    ConceptInSource=concept,
                    ):

                args.writer.add_cognate(
                        lexeme=lexeme,
                        Cognateset_ID=cogid,
                        Cognate_Detection_Method="expert",
                        Source="Girard1971"
                        )