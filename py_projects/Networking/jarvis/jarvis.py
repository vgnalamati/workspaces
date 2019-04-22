from main import cli

if __name__ == '__main__':
    args = cli()
    args.func(args)
