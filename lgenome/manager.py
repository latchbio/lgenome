import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class GenomeData:
    gtf: str
    ref_genome: str
    ref_trans: Optional[str]
    salmon_index: Optional[str]
    STAR_index: Optional[str]


def run(cmd: List[str]):
    subprocess.run(cmd, check=True)


GenomeRegistry = {
    "RefSeq_hg38_p14": GenomeData(
        gtf="s3://latch-genomes/Homo_sapiens/RefSeq/GRCh38.p14/GCF_000001405.40_GRCh38.p14_genomic.stripped.gtf",
        ref_genome="s3://latch-genomes/Homo_sapiens/RefSeq/GRCh38.p14/GCF_000001405.40_GRCh38.p14_genomic.fna",
        ref_trans="s3://latch-genomes/Homo_sapiens/RefSeq/GRCh38.p14/GCF_000001405.40_GRCh38.p14_genomic.transcripts.decoy.fna",
        salmon_index="s3://latch-genomes/Homo_sapiens/RefSeq/GRCh38.p14/salmon_index/",
        STAR_index="s3://latch-genomes/Homo_sapiens/RefSeq/GRCh38.p14/STAR_index/",
    )
}


class NoGenomeRegisteredException(Exception):
    pass


class NoGenomeDataFoundException(Exception):
    pass


class GenomeManager:
    def __init__(self, gid: str):

        # TODO (kenny) check valid gids.
        self._gid = gid

    def download_gtf(self) -> Path:

        g_data = GenomeRegistry.get(self._gid)
        if g_data is None:
            raise NoGenomeRegisteredException(
                f"{self._gid} is not registered with the GenomeManager."
            )

        gtf = g_data.gtf
        if gtf is None:
            raise NoGenomeDataFoundException(
                f"There is no GTF resource stored for {self._gid} within the GenomeManager."
            )

        local_gtf = Path.cwd() / Path(urlparse(gtf).path).name

        run(
            [
                "aws",
                "s3",
                "cp",
                gtf,
                str(local_gtf.resolve()),
            ]
        )

        return local_gtf
