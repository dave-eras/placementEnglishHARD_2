from urllib.parse import urlparse

import streamlit as st

from src.models import TestPage


def _is_audio_url(value: str) -> bool:
    path = urlparse(value).path.lower()
    return path.endswith((".mp3", ".wav", ".m4a", ".ogg"))


def render_stimulus(page: TestPage) -> None:
    if page.input_text:
        if _is_audio_url(page.input_text):
            st.audio(page.input_text)
        else:
            st.markdown(f"**{page.input_text}**")

    st.markdown(page.question_text.replace("\n", "  \n"))


def render_mcq_page(
    page: TestPage,
    form_key: str,
    selected_answer: str | None = None,
    disabled: bool = False,
) -> str | None:
    if page.option_set is None:
        return None

    options = [text for _, text in page.option_set.options]
    index = options.index(selected_answer) if selected_answer in options else None
    return st.radio(
        "Choose one answer:",
        options,
        index=index,
        key=f"{form_key}_mcq",
        disabled=disabled,
    )


def render_dropdown_page(
    page: TestPage,
    form_key: str,
    selected_letters: str | None = None,
    disabled: bool = False,
) -> str | None:
    responses: list[str] = []

    for gap in page.gap_option_sets:
        labels = [f"{letter}) {text}" for letter, text in gap.options]
        selected_label = None
        if selected_letters and len(selected_letters) >= gap.gap_number:
            selected_letter = selected_letters[gap.gap_number - 1]
            selected_label = next((label for label in labels if label.startswith(f"{selected_letter})")), None)

        index = labels.index(selected_label) if selected_label in labels else None
        response = st.selectbox(
            f"Gap {gap.gap_number}",
            labels,
            index=index,
            key=f"{form_key}_gap_{gap.gap_number}",
            disabled=disabled,
        )
        if response:
            responses.append(response[0])

    return "".join(responses) if len(responses) == len(page.gap_option_sets) else None
