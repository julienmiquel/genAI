from vertexai.preview.vision_models import Image, ImageGenerationModel
import traceback

# @title Helper functions
# Wrapper around the Vertex AI SDK to return PIL images
def imagen_generate(
    prompt: str,
    image_model, 
    negative_prompt = "",
    sampleImageSize = 256, # "256", "1024", "1536"
    sampleCount = 1,
    #model_name = "imagegeneration@005",
    seed=None,
):
    #model = ImageGenerationModel.from_pretrained(model_name)

    generate_response = image_model.generate_images(
        prompt=prompt,
        negative_prompt=negative_prompt,
        number_of_images=sampleCount,
        guidance_scale=float(sampleImageSize),
        seed=seed,
    )

    images = []
    for index, result in enumerate(generate_response):
        images.append(generate_response[index]._pil_image)
    return images, generate_response


# Update function called by Gradio
def update(
    model_name,
    prompt,
    negative_prompt,
    sampleImageSize="1536",
    sampleCount=4,
    seed=None,
):
    if len(negative_prompt) == 0:
        negative_prompt = None

    print("prompt:", prompt)
    print("negative_prompt:", negative_prompt)

    # Advanced option, try different the seed numbers
    # any random integer number range: (0, 2147483647)
    if seed < 0 or seed > 2147483647:
        seed = None

    # Use & provide a seed, if possible, so that we can reproduce the results when needed.
    images = []
    error_message = ""
    try:
        images, generate_response = imagen_generate(
            model_name, prompt, negative_prompt, sampleImageSize, sampleCount, seed
        )
    except Exception as e:
        print(e)
        error_message = """An error occured calling the API.
      1. Check if response was not blocked based on policy violation, check if the UI behaves the same way.
      2. Try a different prompt to see if that was the problem.
      """
        error_message += "\n" + traceback.format_exc()
        # raise gr.Error(str(e))

    return images, error_message



examples = [
    [
        "imagegeneration@005",
        """A studio portrait of a man with a grizzly beard eating a sandwich with his hands, a dramatic skewed angled photography, film noir.""",
        "",
        "1536",
        4,
        -1,
    ],
    [
        "imagegeneration@005",
        """A mosaic-inspired portrait of a person, their features formed by a collection of small, colourful tiles.""",
        "",
        "1536",
        4,
        -1,
    ],
    [
        "imagegeneration@005",
        """A modern house on a coastal cliff, sunset, reflections in the water, bright stylized, architectural magazine photo.""",
        "",
        "1536",
        4,
        -1,
    ],
    [
        "imagegeneration@005",
        """Isometric 3d rendering of a car driving in the countryside surrounded by trees, bright colors, puffy clouds overhead.""",
        "",
        "1536",
        4,
        -1,
    ],
    [
        "imagegeneration@005",
        """A tube of toothpaste with the words "CYMBAL" written on it, on a bathroom counter, advertisement.""",
        "",
        "1536",
        4,
        -1,
    ],
    [
        "imagegeneration@005",
        """A cup of strawberry yogurt with the word "Delicious" written on its side, sitting on a wooden tabletop. Next to the cup of yogurt is a plat with toast and a glass of orange juice.""",
        "",
        "1536",
        4,
        -1,
    ],
    [
        "imagegeneration@005",
        """A clearn minimal emblem style logo for an ice cream shop, cream background.""",
        "",
        "1536",
        4,
        -1,
    ],
    [
        "imagegeneration@005",
        """An abstract logo representing intelligence for an enterprise AI platform, "Vertex AI" written under the logo.""",
        "",
        "1536",
        4,
        -1,
    ],
    [
        "imagegeneration@002",
        """A line drawing of a duck boat tour in Boston, with a colorful background of the city.""",
        "",
        "1024",
        4,
        -1,
    ],
    [
        "imagegeneration@002",
        """A raccoon wearing formal clothes, wearing a top hat. Oil painting in the style of Vincent Van Gogh.""",
        "",
        "1024",
        4,
        -1,
    ],
]