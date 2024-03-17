import pickle


def obj_to_file(obj, out_path=None):
    if out_path is None:
        out_path = "output\\obj.pickle"

    with open(out_path, "wb") as f:
        pickle.dump(obj, f)


def file_to_obj(in_path=None):
    if in_path is None:
        in_path = "obj.pickle"

    with open(in_path, "rb") as f:
        obj = pickle.load(f)  # 復元

    return obj
