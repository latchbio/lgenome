import os
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


class NoGenomeResourceFoundException(Exception):
    pass


class GenomeManager:
    def __init__(self, gid: str):

        # TODO (kenny) check valid gids.
        self._gid = gid

    def get_genome_data(self) -> GenomeData:

        g_data = GenomeRegistry.get(self._gid)
        if g_data is None:
            raise NoGenomeRegisteredException(
                f"{self._gid} is not registered with the GenomeManager."
            )
        return g_data

    def download_gtf(self) -> Path:

        g_data = self.get_genome_data()

        gtf = g_data.gtf
        if gtf is None:
            raise NoGenomeResourceFoundException(
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

    def download_ref_genome(self) -> Path:

        g_data = self.get_genome_data()

        ref_genome = g_data.ref_genome
        if ref_genome is None:
            raise NoGenomeResourceFoundException(
                f"There is no reference genome resource stored for {self._gid} within the GenomeManager."
            )

        local_ref_genome = Path.cwd() / Path(urlparse(ref_genome).path).name

        run(
            [
                "aws",
                "s3",
                "cp",
                ref_genome,
                str(local_ref_genome.resolve()),
            ]
        )

        return local_ref_genome

    def download_ref_trans(self) -> Path:

        g_data = self.get_genome_data()

        ref_trans = g_data.ref_trans
        if ref_trans is None:
            raise NoGenomeResourceFoundException(
                f"There is no reference transcriptome resource stored for {self._gid} within the GenomeManager."
            )

        local_ref_trans = Path.cwd() / Path(urlparse(ref_trans).path).name

        run(
            [
                "aws",
                "s3",
                "cp",
                ref_trans,
                str(local_ref_trans.resolve()),
            ]
        )

        return local_ref_trans

    def download_salmon_index(self) -> Path:

        g_data = self.get_genome_data()

        salmon_index = g_data.salmon_index
        if salmon_index is None:
            raise NoGenomeResourceFoundException(
                f"There is no salmon index resource stored for {self._gid} within the GenomeManager."
            )

        os.mkdir("salmon_index")
        local_salmon_index = Path("salmon_index").resolve()
        run(
            [
                "aws",
                "s3",
                "sync",
                salmon_index,
                str(local_salmon_index),
            ]
        )

        return local_salmon_index

    def download_STAR_index(self) -> Path:

        g_data = self.get_genome_data()

        STAR_index = g_data.STAR_index
        if STAR_index is None:
            raise NoGenomeResourceFoundException(
                f"There is no STAR index resource stored for {self._gid} within the GenomeManager."
            )

        os.mkdir("STAR_index")
        local_STAR_index = Path("STAR_index").resolve()
        run(
            [
                "aws",
                "s3",
                "sync",
                STAR_index,
                str(local_STAR_index),
            ]
        )

        return local_STAR_index
