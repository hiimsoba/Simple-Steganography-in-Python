import cv2
import sys

# sets p'th bit to b in n ( not confusing at all. )
def modify_bit(n, p, b):
    mask = 1 << p
    return (n & ~mask) | ((b << p) & mask)

# can you read, motherfucker? CAN YOU READ?
def read_nth_bit(n, k):
    bit = n & (1 << k)
    # ternary operators didn't work, i guess i'm gay
    if bit == 0:
        return 0
    else:
        return 1

# turns an ASCII string to a binary string
def ascii_to_binary(string):
    return ''.join([format(ord(char),'#010b')[2:] for char in string])

# turns a binary string to an ASCII string
def binary_to_ascii(string):
    return ''.join([chr(int(string[i:i + 8], 2)) for i in range(0, len(string), 8)])

# "hides" a string ( called "secret" ) into the image
def encode_string_in_image(secret, img):
    # secret turned to binary!
    binary_secret = ascii_to_binary(secret)

    # and add a NULL byte, so we know when to stop decoding
    binary_secret += "00000000"

    # height of image is shape[0]
    h = img.shape[0]

    # width is shape[1]
    w = img.shape[1]

    # and there's three channels for each pixel (R, G, B)
    c = img.shape[2]

    # keep track of the current y ( height ), x ( width ) and c ( channel )
    curr_h = 0
    curr_w = 0
    curr_c = 0
    curr_bit = 0

    # for each bit in the binary secret
    for i in range(len(binary_secret)):
        # current bit
        bit = int(binary_secret[i])

        # set the nth bit to the current bit in the image
        img[curr_h][curr_w][curr_c] = modify_bit(img[curr_h][curr_w][curr_c], curr_bit, bit)

        # increase the channel
        curr_c += 1
        # if the channel is equal to the number of channels
        # increase the x
        if curr_c == c:
            curr_c = 0
            curr_w += 1
            # if x is equal to the width of the image, increase y
            if curr_w == w:
                curr_w = 0
                curr_h += 1
                # and if y is at the bottom of the image
                if curr_h == h:
                    # go to the next bit
                    curr_bit += 1
                    curr_h = 0
                    # and if we reached the 8th bit ( since there are values between 0-255, so only 8 bits )
                    # break out of the looperino
                    if curr_bit == 8:
                        return "incomplete"
    return "complete"

# gets and image and the number of bits to decode
# if the number of bits is not given, it will return
# all the LSBs from the image
def decode_string_from_image(img):
    # the data we'll recover from the image
    secret = ""

    # height of image is shape[0]
    h = img.shape[0]

    # width is shape[1]
    w = img.shape[1]

    # and there's three channels for each pixel (R, G, B)
    c = img.shape[2]

    # keep track of the current y ( height ), x ( width ) and c ( channel )
    curr_h = 0
    curr_w = 0
    curr_c = 0
    curr_bit = 0

    # for each bit in the image
    while True:
        # first check if the last 8 bits of the decoded secret are equal to the NULL byte
        # this means we reached the end of the encoded message
        if len(secret) % 8 == 0 and secret[-8:] == "00000000":
            break

        # add the current LSB to the secret
        secret += str(read_nth_bit(img[curr_h][curr_w][curr_c], curr_bit))

        # increase the channel
        curr_c += 1
        # if the channel is the number of channels
        # increase the x
        if curr_c == c:
            curr_c = 0
            curr_w += 1
            # if x is the width of the image, increase y
            if curr_w == w:
                curr_w = 0
                curr_h += 1
                # and if y is at the bottom of the image
                # break out of the loop
                # we can't add any more data
                if curr_h == h:
                    # go to the next bit
                    curr_bit += 1
                    curr_h = 0
                    # and if we reached the 7th bit ( since there are values between 0-255, so only 8 bits )
                    # break out of the looperino
                    if curr_bit == 7:
                        break
    # return the result, as a binary string
    return str(secret)

if __name__ == '__main__':
    # get the arguments
    args = sys.argv[1:]

    # first check if there are arguments provided...
    if len(args) == 0:
        print("No arguments provided, pendejo!")
        quit()

    # first, check if there's a single argument -- the help flag
    if args[0] == "-help":
        print("\nTo encode a string into an image:")
        print("  python steg.py -encode -console <inp_string> <in_img_fname> <out_img_fname>")
        print("  python steg.py -encode -file <in_string_fname> <in_img_fname> <out_img_fname>")
        print()
        print("To decode a string from an image:")
        print("  python steg.py -decode <in_img_fname>")
        print("  python steg.py -decode <in_img_fname> <out_string_fname>")
        print("\nBY THE WAY... save the output files as PNG. Otherwise the message is probably gonna be lost due to compression")
        quit()

    # there's always gonna be at least two arguments
    if len(args) < 2:
        print("not enough arguments provided")
        quit()
    
    # now, we can proceed getting the arguments

    # the option ( decode / encode ) is the first argument. always.
    option = args[0]

    if not(option == "-encode" or option == "-decode"):
        print("illegal first argument")
        quit()

    # now, if the option is encode
    if option == "-encode":
        # we will always need 4 arguments ( beside the "encode", so 5 in total )
        if len(args) < 5:
            print("not enough arguments provided for encoding")
            quit()

        # if we have all the required arguments, we can get the second argument
        # which is a flag of whether we get the string from the console or from a file
        input_flag = args[1]

        if input_flag == "-file":
            input_flag = 1
        elif input_flag == "-console":
            input_flag = 0
        else:
            # if we got here, then the second argument is invalid, we tell the user to fuck off
            print("illegal second argument, should be \"-file\" or \"-console\"")
            quit()

        # good, now we know if we want to read from the file or from the console
        
        # if it's 0, we read from the console, it's EZ!
        if input_flag == 0:
            input_string = args[2]
        elif input_flag == 1:
            # otherwise try to read from the file
            # if we get an exception, show a message and quit
            try:
                with open(args[2], 'r') as myfile:
                    input_string = myfile.read()
            except:
                print("exception caught trying to read from the input string file provided")
                quit()

        # if we got here with no errors, we're fucking geniuses, we can now grab the input image
        # so the forth argument ( i think ) is gonna be the filename of the input image
        image = cv2.imread(args[3])

        if image is None:
            print("image is none, make sure the image file exists and is not empty, i guess")
            quit()

        # and if we got here, one final step, boom.
        # encode the string in the image
        result = encode_string_in_image(input_string, image)

        # and save it with the given output filename
        cv2.imwrite(args[4], image)

        # and print to the console that the operation succedeed or some stuff...
        print("\n\nfinished encoding! O:")
        if (result == "incomplete"):
            print("...tho it's kinda not complete...")

    elif option == "-decode":
        # now, if the option is decode, we have two different ways to parse this
        # we either have 3 arguments and we write the output string to the console
        # or we have 4 arguments and the user will have to provide a filename for the output string

        # first argument will always be the input image filename, so we do same as earlier
        image = cv2.imread(args[1])

        if image is None:
            print("image is none, make sure the image file exists and is not empty, i guess")
            quit()

        # get the decoded string from the image
        result = decode_string_from_image(image)

        # now check if there's also the 3rd argument, to print to a file instead of the console
        if len(args) == 3:
            output_file = open(args[2], "w")
            output_file.write(binary_to_ascii(result))
            output_file.close()
        else:
            # otherwise, print to the console. done.
            print(binary_to_ascii(result))

        # and print to the console that the operation succedeed or some stuff...
        print("\n\nfinished decoding! O:")