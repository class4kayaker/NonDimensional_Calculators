import pytest
import click.testing
import sci_parameter_utils.cli as prm_cli


@pytest.mark.parametrize(
    'parser,args,stdout', [
    ],
    indirect=['parser']
)
def test_searcher(parser, args, stdout):
    res = click.testing.CliRunner.invoke(prm_cli.print_vals, args=args)
    assert res.output == stdout
