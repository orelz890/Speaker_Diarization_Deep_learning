import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--in-lab-path', type=str, help="Input lab path")
    parser.add_argument('--out-regular-lab-path', type=str, help="Output lab path")
    parser.add_argument('--out-overlap-lab-path', type=str, help="Output lab path")

    args = parser.parse_args()

    with open(args.in_lab_path, "r") as reader:
        with open(args.out_regular_lab_path, "w") as reg_writer:
            with open(args.out_overlap_lab_path, "w") as over_writer:
                for x in reader:
                    data = x.split('\t')
                    if bool(data[3]):
                        over_writer.write(x)
                    else:
                        reg_writer.write(x)


