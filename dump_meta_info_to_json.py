from util import load_id2obj_dict, json_dump


def main():
    import argparse

    parser = argparse.ArgumentParser("Dump meta information to json")

    parser.add_argument('--interactions_path',
                        required=True)
    parser.add_argument('--interactions_output_path',
                        required=True)
    parser.add_argument('--people_path',
                        required=True)
    parser.add_argument('--people_output_path',
                        required=True)
    args = parser.parse_args()

    json_dump(
        load_id2obj_dict(args.interactions_path, 'message_id'),
        args.interactions_output_path
    )
    json_dump(
        load_id2obj_dict(args.people_path, 'id'),
        args.people_output_path
    )


if __name__ == '__main__':
    main()
