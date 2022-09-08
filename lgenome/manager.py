import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse
from warnings import warn

from dataclasses_json import dataclass_json


def run(cmd: List[str]):
    full_command = " ".join(cmd)
    print(f"Running '{full_command}'")
    subprocess.run(cmd, check=True)


class LGenomeBackend:
    def cp(self, src: str, dst: str, *, show_progress: bool = True):
        raise NotImplementedError()

    def sync(self, src: str, dst: str, *, show_progress: bool = True):
        raise NotImplementedError()


class LGenomeS5cmdBackend(LGenomeBackend):
    def cp(self, src: str, dst: str, *, show_progress: bool = True):
        run(["s5cmd", "cp", src, dst])

    def sync(self, src: str, dst: str, *, show_progress: bool = True):
        run(["s5cmd", "sync", src + "*", dst])


class LGenomeS3Backend(LGenomeBackend):
    def cp(self, src: str, dst: str, *, show_progress: bool = True):
        cmd = ["aws", "s3", "cp", src, dst]
        if not show_progress:
            cmd.append("--no-progress")
        run(cmd)

    def sync(self, src: str, dst: str, *, show_progress: bool = True):
        cmd = ["aws", "s3", "sync", src, dst]
        if not show_progress:
            cmd.append("--no-progress")
        run(cmd)


@dataclass_json
@dataclass
class GenomeData:
    gtf: str
    ref_genome: str
    ref_trans: Optional[str]
    salmon_index: Optional[str]


GenomeRegistry = {
    "RefSeq_hg38_p14": GenomeData(
        gtf="s3://latch-genomes/Homo_sapiens/RefSeq/GRCh38.p14/GCF_000001405.40_GRCh38.p14_genomic.stripped.gtf",
        ref_genome="s3://latch-genomes/Homo_sapiens/RefSeq/GRCh38.p14/GCF_000001405.40_GRCh38.p14_genomic.fna",
        ref_trans="s3://latch-genomes/Homo_sapiens/RefSeq/GRCh38.p14/GCF_000001405.40_GRCh38.p14_genomic.transcripts.decoy.fna",
        salmon_index="s3://latch-genomes/Homo_sapiens/RefSeq/GRCh38.p14/salmon_index/",
    ),
    "RefSeq_T2T_CHM13v2_0": GenomeData(
        gtf="s3://latch-genomes/Homo_sapiens/RefSeq/T2T_CHM13v2_0/stripped.gtf",
        ref_genome="s3://latch-genomes/Homo_sapiens/RefSeq/T2T_CHM13v2_0/genome.fna",
        ref_trans="s3://latch-genomes/Homo_sapiens/RefSeq/T2T_CHM13v2_0/genome.transcripts.fa",
        salmon_index="s3://latch-genomes/Homo_sapiens/RefSeq/T2T_CHM13v2_0/salmon_index/",
    ),
    "RefSeq_R64": GenomeData(
        gtf="s3://latch-genomes/Saccharomyces cerevisiae/RefSeq/R64/stripped.gtf",
        ref_genome="s3://latch-genomes/Saccharomyces cerevisiae/RefSeq/R64/genome.fna",
        ref_trans="s3://latch-genomes/Saccharomyces cerevisiae/RefSeq/R64/genome.transcripts.fa",
        salmon_index="s3://latch-genomes/Saccharomyces cerevisiae/RefSeq/R64/salmon_index/",
    ),
    "RefSeq_GRCm39": GenomeData(
        gtf="s3://latch-genomes/Mus musculus/RefSeq/GRCm39/stripped.gtf",
        ref_genome="s3://latch-genomes/Mus musculus/RefSeq/GRCm39/genome.fna",
        ref_trans="s3://latch-genomes/Mus musculus/RefSeq/GRCm39/genome.transcripts.fa",
        salmon_index="s3://latch-genomes/Mus musculus/RefSeq/GRCm39/salmon_index/",
    ),
}


class NoGenomeRegisteredException(Exception):
    pass


class NoGenomeResourceFoundException(Exception):
    pass


class GenomeManager:
    def __init__(self, gid: str, *, backend: Optional[LGenomeBackend] = None):

        # TODO (kenny) check valid gids.
        self._gid = gid

        self.backend = None
        if self.backend is None:
            if shutil.which("s5cmd") is not None:
                self.backend = LGenomeS5cmdBackend()
            if shutil.which("s3") is not None:
                self.backend = LGenomeS3Backend()

        if self.backend is None:
            warn(
                "No available lgenome backend - install an appropriate blobstore CLI (eg. s3 or s5cmd.)"
            )

    def get_genome_data(self) -> GenomeData:

        g_data = GenomeRegistry.get(self._gid)
        if g_data is None:
            raise NoGenomeRegisteredException(
                f"{self._gid} is not registered with the GenomeManager."
            )
        return g_data

    def download_gtf(self, show_progress: bool = False) -> Path:

        g_data = self.get_genome_data()

        gtf = g_data.gtf
        if gtf is None:
            raise NoGenomeResourceFoundException(
                f"There is no GTF resource stored for {self._gid} within the GenomeManager."
            )

        local_gtf = Path.cwd() / Path(urlparse(gtf).path).name

        assert self.backend is not None
        self.backend.cp(gtf, str(local_gtf.resolve()), show_progress=show_progress)

        return local_gtf

    def download_ref_genome(self) -> Path:

        g_data = self.get_genome_data()

        ref_genome = g_data.ref_genome
        if ref_genome is None:
            raise NoGenomeResourceFoundException(
                f"There is no reference genome resource stored for {self._gid} within the GenomeManager."
            )

        local_ref_genome = Path.cwd() / Path(urlparse(ref_genome).path).name

        assert self.backend is not None
        self.backend.cp(ref_genome, str(local_ref_genome.resolve()))

        return local_ref_genome

    def download_ref_trans(self) -> Path:

        g_data = self.get_genome_data()

        ref_trans = g_data.ref_trans
        if ref_trans is None:
            raise NoGenomeResourceFoundException(
                f"There is no reference transcriptome resource stored for {self._gid} within the GenomeManager."
            )

        local_ref_trans = Path.cwd() / Path(urlparse(ref_trans).path).name

        assert self.backend is not None
        self.backend.cp(ref_trans, str(local_ref_trans.resolve()))

        return local_ref_trans

    def download_salmon_index(self, show_progress: bool = True) -> Path:

        g_data = self.get_genome_data()

        salmon_index = g_data.salmon_index
        if salmon_index is None:
            raise NoGenomeResourceFoundException(
                f"There is no salmon index resource stored for {self._gid} within the GenomeManager."
            )

        os.mkdir("salmon_index")
        local_salmon_index = Path("salmon_index").resolve()

        assert self.backend is not None
        self.backend.sync(
            salmon_index, str(local_salmon_index), show_progress=show_progress
        )

        return local_salmon_index
