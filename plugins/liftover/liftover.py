from liftover import get_lifter


def liftover(text: str) -> str:
    converter = get_lifter('hg19', 'hg38')
    chrom = '1'
    pos = int(text)

    return converter[chrom][pos][0][1]