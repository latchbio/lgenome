genome
---

A python package to manage curated genomic resources for bioinformatics workflows.

### Introduction

This library is a lightweight wrapper over AWS S3.

For each genome managed by [latch](latch.bio), a collection of URLS pointing to well-defined
"genome resources" is maintained. The schema holding these URLS is stable across
managed genomes and can be represented by the below class. 

```
class GenomeData:
    gtf: str
    ref_genome: str
    ref_trans: Optional[str]
    salmon_index: Optional[str]
    STAR_index: Optional[str]
```

Genome resources themself, eg. a reference genome, can be retrieved through a standardized interface.

* `def download_gtf(self) -> Path`
* `def download_ref_genome(self) -> Path`
* `def download_ref_trans(self) -> Path`
* `def download_salmon_index(self) -> Path`
* `def download_star_index(self) -> Path`

There really isn't much else to this.
