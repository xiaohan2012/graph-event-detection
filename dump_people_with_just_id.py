import pandas as pd

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--interaction_path', required=True)
    parser.add_argument('-o', '--output_path', required=True)

    args = parser.parse_args()
    df = pd.read_pickle(args.interaction_path)

    people = set()
    for i, r in df.iterrows():
        people.add(r['sender_id'])
        for id_ in r['recipient_ids']:
            people.add(id_)

    new_df = pd.DataFrame({'id': list(people)})
    new_df.to_pickle(args.output_path)

if __name__ == "__main__":
    main()
    
    

