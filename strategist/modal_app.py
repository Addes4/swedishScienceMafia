"""Fan strategist jobs out on Modal (app `ssm-strategist-v2`). Used by `python -m strategist.v2 ... --modal`.

Each job is one (benchmark, seed) with all its arms, or one fork job; jobs are pure functions of their
arguments, so the order in which results come back does not matter. The strategist package is
standard-library Python and is shipped to the container as local source.
"""
import modal

app = modal.App('ssm-strategist-v2')
image = modal.Image.debian_slim(python_version='3.12').add_local_python_source('strategist')
CHUNK = 4          # jobs per call: amortises call overhead for the short run jobs


@app.function(image=image, cpu=1.0, memory=1024, timeout=3600, max_containers=60, retries=2)
def run_jobs(jobs):
    from strategist.v2 import dispatch
    return [dispatch(job) for job in jobs]


def map_jobs(jobs, chunk=CHUNK):
    """Yields one result list per job (in completion order of the chunks)."""
    chunks = [jobs[i:i+chunk] for i in range(0, len(jobs), chunk)]
    with app.run():
        for results in run_jobs.map(chunks, order_outputs=False):
            yield from results
