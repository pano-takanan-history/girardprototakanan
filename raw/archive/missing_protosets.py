from lingpy import Wordlist


proto_sets = []


wl = Wordlist.from_cldf(
    "cldf/cldf-metadata.json",
    # columns to be loaded from CLDF set
    columns=(
        "language_id",
        "language_core",
        "concept_name",
        "segments",
        "form",
        "protoset"
        ),
    # a list of tuples of source and target
    namespace=(
        ("language_id", "doculect"),
        ("concept_name", "concept"),
        ("segments", "tokens")
        )
    )

for idx in wl:
    if wl[idx, "protoset"] not in proto_sets:
        # print(wl[idx, "protoset"])
        proto_sets.append(wl[idx, "protoset"])
# print(proto_sets)

missing = []
for i in range(504):
    if str(i) not in proto_sets:
        missing.append(i)
print(missing)
