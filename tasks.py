from invoke import run, task


@task
def test(f=False, v=False):
    if f:
        run('flake8 *.py **/**.py  --exclude=build/* --exit-zero')
    verbose = ''
    if v:
        verbose = ' -vv'
    run('py.test%s -s tests/tests.py --cov=ascii2graph --cov-report term-missing' % verbose, pty=True)  # noqa
    #run('py.test%s -s tests/tests/tests.py --cov=ascii2graph --cov-report term-missing --capture=sys' % verbose, pty=True)  # noqa
