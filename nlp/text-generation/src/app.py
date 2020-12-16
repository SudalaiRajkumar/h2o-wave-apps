from h2o_wave import main, app, Q, ui, copy_expando
from transformers import pipeline

async def init(q: Q):
    if not q.client.app_initialized:
        q.app.model = pipeline("text-generation")
        q.client.app_initialized = True

    q.page.drop()

    q.page["title"] = ui.header_card(
        box="1 1 8 1",
        title="Text Generation",
        subtitle="Generate text using Huggingface pipelines",
        icon="AddNotes",
        icon_color="Blue",
    )

async def get_inputs(q: Q):
    q.page['main'] = ui.form_card(box="1 2 8 5", items=[
        ui.text_xl('Enter your text input for generation:'),
        ui.textbox(name="input_text",
                   label='',
                   value=q.app.input_text,
                   multiline=True),
        ui.separator(),
        ui.slider(name="num_words_to_generate",
                  label="Maximum number of words to generate (including input text)",
                  min=5,
                  max=50,
                  step=1,
                  value=q.app.num_words_to_generate if q.app.num_words_to_generate else 12,
                  ),
        ui.separator(),
        ui.buttons([ui.button(name="generate_text", label='Generate', primary=True),
                    ])
    ])

async def show_results(q: Q):
    q.page['main'] = ui.form_card(box="1 2 4 5", items=[
        ui.text_xl("Input Text:"),
        ui.separator(),
        ui.text(q.app.input_text),
        ui.separator(),
        ui.buttons([ui.button(name="get_inputs", label='Try Again!', primary=True),
                    ])
    ])

    result = q.app.model(q.app.input_text, max_length=q.app.num_words_to_generate, do_sample=False)[0]
    q.app.generated_text = result["generated_text"]
    q.page['visualization'] = ui.form_card(box="5 2 4 5", items=[
        ui.text_xl("Generated Text:"),
        ui.separator(''),
        ui.text(q.app.generated_text)
    ])

@app("/")
async def serve(q: Q):
    await init(q)
    if q.args.generate_text:
        copy_expando(q.args, q.app)
        await show_results(q)
    else:
        await get_inputs(q)
    await q.page.save()
