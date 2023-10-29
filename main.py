import crawler

def main(url):
    pass

if __name__ == "__main__":
    try:
        url = sys.argv[1]
    except IndexError:
        print("Please input an URL!")
    main(url)
