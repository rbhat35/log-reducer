import uuid
import click


def normal_to_yang_uuid(n_uuid):
    """Converts yang's uuid to a normal uuid.
    yang - 240 9 156 0 0 0 0 0 0 0 0 0 0 0 0 32
    normal - f0099c00-0000-0000-0000-000000000020
    """
    normal = uuid.UUID(n_uuid) if type(str(n_uuid)) is str else n_uuid
    return ' '.join([str(ord(b)) for b in normal.bytes])


def yang_to_normal_uuid(yang_uuid):
    """Converts yang's uuid to a normal uuid."""
    return uuid.UUID(bytes=''.join([chr(int(b)) for b in yang_uuid.split(' ')]))


@click.group()
def cli():
    pass


@cli.command("y2n")
@click.argument("uuid", required=True)
def y2n(uuid):
    """ Convert a yang uuid to a normal uuid and print."""

    print yang_to_normal_uuid(uuid)


@cli.command("uuid-split")
@click.argument("host-obj", required=True)
def uuid_split(host_obj):
    """Return host and object uuid.
       @host-obj -- host-object uuid.

       ex: "128 55 12 110 82 84 0 240 8 96 0 0 0 0 0 112-1 0 208 15 40 9 24 0 0 0 0 0 209 153 215 91"
    """
    host, obj = host_obj.split('-')
    print yang_to_normal_uuid(obj), yang_to_normal_uuid(host)


def main():
    cli()

if __name__ == '__main__':
    main()
