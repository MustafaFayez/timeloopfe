import os
import sys
import logging
import timeloopfe as tl
import timeloopfe.v4spec as v4spec
from timeloopfe.processors.v4_standard_suite import EnableDummyTableProcessor


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    OPTIONS = {
        0: "eyeriss_like",
        1: "eyeriss_nested_hierarchy",
        2: "simba_like",
        3: "simple_output_stationary",
        4: "simple_pim",
        5: "simple_weight_stationary",
        6: "sparse_tensor_core_like",
        7: "sparseloop/01.2.1-DUDU-dot-product",
        8: "sparseloop/01.2.2-SUDU-dot-product",
        9: "sparseloop/01.2.3-SCDU-dot-product",
        10: "sparseloop/01.2.1-DUDU-dot-product",
        11: "sparseloop/02.2.1-spMspM",
        12: "sparseloop/02.2.2-spMspM-tiled",
        13: "sparseloop/03.2.1-conv1d",
        14: "sparseloop/03.2.2-conv1d+oc",
        15: "sparseloop/03.2.3-conv1d+oc-spatial",
        16: "sparseloop/04.2.1-eyeriss-like-gating",
        17: "sparseloop/04.2.2-eyeriss-like-gating-mapspace-search",
        18: "sparseloop/04.2.3-eyeriss-like-onchip-compression",
        19: "raella",
        20: "a100",
    }

    CHOICE = 20
    SPLIT = True
    m = sys.argv[1]
    n = sys.argv[2]
    k = sys.argv[3]

    assert (
        CHOICE in OPTIONS
    ), f'Invalid choice "{CHOICE}". Choose from {list(OPTIONS.keys())}'

    cinstr = "_split" if SPLIT else ""
    TARGET = [f"{OPTIONS[CHOICE]}/arch{cinstr}_{m}_{n}_{k}", f"{OPTIONS[CHOICE]}/problem_{m}_{n}_{k}", "mapper"]
    TARGET = [os.path.join("arch_spec_examples", f"{t}.yaml") for t in TARGET]

    # alt_prob = f"problem_{OPTIONS[CHOICE]}"
    # if os.path.exists(TARGET[1].replace("problem", alt_prob)):
    #     TARGET[1] = TARGET[1].replace("problem", alt_prob)

    # Add in some extra files for Sparseloop inputs
    if "sparseloop" in OPTIONS[CHOICE]:
        TARGET = TARGET[:1]
        for f in os.listdir(os.path.dirname(TARGET[0])):
            if "arch" not in f:
                TARGET.append(os.path.join(os.path.dirname(TARGET[0]), f))

    for_model = CHOICE >= 7 and CHOICE != 17 and CHOICE != 19 and CHOICE != 20

    print(tl.parsing.doc.get_property_tree(v4spec.Specification))
    spec = v4spec.Specification.from_yaml_files(*TARGET)
    spec.process()
    # Add in the EnableDummyTable processor so Accelergy provides dummy numbers
    # and we don't have to worry about having area/energy estimators
    spec.process(EnableDummyTableProcessor)

    # for_model = True
    # Run the mapper or model
    if for_model:
        tl.model(spec, "./outdir_"+OPTIONS[CHOICE]+"/"+m+"_"+n+"_"+k+"/")
    else:
        tl.mapper(spec, "./outdir_"+OPTIONS[CHOICE]+"/"+m+"_"+n+"_"+k+"/")
