import html
import uuid
from pathlib import Path

import streamlit as st

from src.csv_loader import load_pages
from src.models import TestPage
from src.renderers import render_dropdown_page, render_mcq_page, render_stimulus
from src.results import ItemResult, load_result_stats
from src.storage import save_response

CSV_PATH = Path(__file__).parent / "English Placement 1.5.csv"
RESULTS_PATH = Path(__file__).parent / "results.xlsx"

# Add hardcoded review explanations here. Use the page item_id as the key,
# for example: "row_02_q_1": "This is correct because ..."
JUSTIFICATIONS: dict[str, str] = {
    "row_01_dropdown": "All to do with appropriacy for a formal negotation requiring diplomacy.",
    "row_02_q_1": "'Fond memories' => 'great day' and some sadness about 'long since vanished' item. 'chocolate bar' => 'from the vending machine, 'clunk' sound, foil wrappers'.",
    "row_02_q_2": "'if one of these turned up in your lunchbox.' (probably made by a parent)",
    "row_02_q_3": "'wistful' = a feeling of longing for something from the past—such as a cherished memory or a time that can no longer be relived",
    "row_02_q_4": "'they all went down the same hole' - a colloquial expression for not caring too much about the quality of what you consume ... requires some understanding of the British food landscape before Jamie Oliver turned up.",
    "row_03_q_1": "'corporate crime doesn't have a mascot ... we think that's wrong ... please meet Crackers, the corporate crime chicken'.",
    "row_03_q_2": "'they got a tax break because they had promised not to eliminate any jobs, which is exactly what they did.' 'they got a tax break ... the guarantee was they were gonna keep jobs in NYC ... they laid off quite a few people.'",
    "row_03_q_3": "'there is clearly a serious message about wrongdoing but the mascot and the music choice are firmly tongue-in-cheek as is the style of humourous satire.",
    "row_04_q_1": "'to the uninitiated (it) may seem as impenetrable as their record covers.' 'Uninitiated' => 'people who don't know much about the band'.",
    "row_04_q_2": "'as a fellow Mancunian''you used to go an see them in Manchester'? Mancunian => someone from Manchester",
    "row_04_q_3": "'I do like them, yeah' ... 'it became so pretentious, I didn't get anywhere near finishing it'.",
    "row_05_q_1": "'when you can't stop yourself from saying something even though you know you shouldn't, so you say it quietly or unclearly.",
    "row_05_q_2": "'break a promise/deal",
    "row_05_q_3": "'share a concern so that it might be observed and discussed",
    "row_05_q_4": "'start playing music'",
    "row_05_q_5": "",
    "row_05_q_6": "'to sound out' = to test the water, to see how someone reacts, 'sound off' = to express an opinion, usually angrily or without being asked",
    "row_07_q_1": "'if someone works all the time, it's kind of like a job ... it's not a job, it's a vocation - you can't feel like creating all the time.' C is too similar to D - will change.",
    "row_07_q_2": "'I staggered back to the bedroom and I stood there and I went 'eurgh' ... oh my god, I've slept in that and it's so dis... it was a million time worse than what people see (in the show).'",
    "row_07_q_3": "hear the tone of her voice 'that's my show for Japan - brilliant, done it.' 'It was theatrical, it was dramatic ... from a distance it was beautiful'.",
    "row_08_q_1": "this is about a show, a film installation which would happen most likely in a gallery.",
    "row_08_q_2": "the humour is in choosing a small unfashionable place with a funny sounding name as a comparison with the USA. The affection towards the ordinary people that live there can be read across the text.",
    "row_08_q_3": "breathlessness is conveyed by the use of commas to list words, often alliterated (same sound at the beginning of each word - grim, grainy, grey). the writer is very enthusiastic and says they could watch hours and hours of it.",
    "row_08_q_4": "hmmm ... too easy eh?",
    "row_08_q_5": "flares are wide trousers people wore in the 70s - the writer makes a play on this being 'the only difference' between now and the problems of the 70s.",
    "row_06_q_1": "Boy King = Tutankhamun, bling-bling = treasure and jewellery, unearthed = discovered ... 'mum's the word' is a way of saying 'don't tell anyone' -> not relevant to the story except as a way to squeez in the word 'mummy'.",
    "row_06_q_2": "Pack yer Raj -> pack your bags (go away), the Raj was the name of the British colonial rule in India. Marching orders = orders to move on, go away.",
    "row_06_q_3": "Bricking it => 'scared', brick (in a wall), hardliners = people who are very strict and don't compromise., red-faced = embarrassed, curtain (iron curtain)",
    "row_06_q_4": "Lunar (of the moon) - tin-can = reference to David Bowie's Space Oddity ... 'ground control to Major Tom' etc., plant stars and stripes = reference to the flag of the USA",
}


def _init_state() -> None:
    defaults = {
        "started": False,
        "completed": False,
        "session_id": None,
        "current_index": 0,
        "viewing_results": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _apply_button_theme() -> None:
    st.markdown(
        """
        <style>
        div.stButton > button[kind="primary"],
        div.stFormSubmitButton > button[kind="primary"] {
            background-color: #0d6efd;
            border-color: #0d6efd;
            color: #ffffff;
        }

        div.stButton > button[kind="primary"]:hover,
        div.stFormSubmitButton > button[kind="primary"]:hover {
            background-color: #0b5ed7;
            border-color: #0a58ca;
            color: #ffffff;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data
def _get_pages(csv_mtime: float) -> list[TestPage]:
    return load_pages(CSV_PATH)


@st.cache_data
def _get_result_stats(results_mtime: float) -> dict[str, ItemResult]:
    return load_result_stats(RESULTS_PATH)


def _render_welcome() -> None:
    st.title("English Placement Test — version 1.5 Pilot")
    st.markdown(
        """
        Welcome - please read:

        - Answer each question, then press **Next** to continue.
        - Use the comment box if you have feedback about an item.
        - This needs to be a fair test, so no googling answers or translating phrases!!!
        - It is completely anonymous.
        """
    )

    start_test = st.button("Start test", type="primary")

    if start_test:
        st.session_state.started = True
        st.session_state.session_id = uuid.uuid4().hex
        st.session_state.current_index = 0
        st.session_state.completed = False
        st.session_state.viewing_results = False
        st.rerun()


def _render_item(page: TestPage, page_number: int, total_pages: int) -> None:
    st.progress(page_number / total_pages)
    st.caption(f"Question {page_number} of {total_pages}")

    form_key = f"{st.session_state.session_id}_{page.item_id}"

    with st.form(form_key, clear_on_submit=True):
        render_stimulus(page)

        if page.item_type == "DropDown":
            response = render_dropdown_page(page, form_key)
        else:
            response = render_mcq_page(page, form_key)

        comment = st.text_area(
            "Any feedback about this item?",
            placeholder="Optional comments for the test team...",
        )
        submitted = st.form_submit_button("Next", type="primary")

    if submitted:
        if not response:
            if page.item_type == "DropDown":
                st.error("Please select an answer for all 4 gaps before submitting.")
            else:
                st.error("Please select an answer before submitting.")
            return

        if page.item_type == "DropDown":
            correct = "".join(gap.correct_letter for gap in page.gap_option_sets)
        else:
            correct = page.option_set.correct_text if page.option_set else ""

        try:
            save_response(
                session_id=st.session_state.session_id,
                item_id=page.item_id,
                test_id=page.test_id,
                row_index=page.row_index,
                sub_index=page.sub_index,
                item_type=page.item_type,
                skill=page.skill,
                response=response,
                correct=correct,
                comment=comment.strip(),
            )
        except Exception as exc:
            st.error(f"Could not save your response. Please try again. ({exc})")
            return

        st.session_state.current_index += 1
        if st.session_state.current_index >= total_pages:
            st.session_state.completed = True
        st.rerun()


def _render_result_chart(result: ItemResult | None) -> None:
    if result is None or result.total_count == 0:
        st.info("No responses recorded for this question yet.")
        return

    correct_percent = result.correct_percent
    incorrect_percent = result.incorrect_percent
    st.html(
        f"""
        <div style="display:flex;align-items:center;gap:1rem;margin:1rem 0 1.5rem;">
            <div style="
                width:150px;
                height:150px;
                border-radius:50%;
                background:conic-gradient(#198754 0 {correct_percent:.2f}%, #dc3545 {correct_percent:.2f}% 100%);
                border:1px solid #d0d7de;
            "></div>
            <div style="font-family:'Source Sans Pro',sans-serif;line-height:1.7;">
                <div><span style="display:inline-block;width:.65rem;height:.65rem;border-radius:50%;background:#198754;"></span> Correct: {correct_percent:.1f}% ({result.correct_count})</div>
                <div><span style="display:inline-block;width:.65rem;height:.65rem;border-radius:50%;background:#dc3545;"></span> Incorrect: {incorrect_percent:.1f}% ({result.incorrect_count})</div>
            </div>
        </div>
        """
    )


def _render_justification(page: TestPage) -> None:
    justification = html.escape(JUSTIFICATIONS.get(page.item_id, ""))
    if not justification:
        justification = "&nbsp;"

    st.html(
        f"""
        <div style="margin:1rem 0;">
            <div style="
                color:#262730;
                font-family:'Source Sans Pro',sans-serif;
                font-size:0.875rem;
                font-weight:600;
                margin-bottom:0.35rem;
            ">Justification</div>
            <div style="
                min-height:140px;
                white-space:pre-wrap;
                line-height:1.5;
                color:#262730;
                background:#ffffff;
                border:1px solid rgba(49, 51, 63, 0.2);
                border-radius:0.5rem;
                padding:0.75rem;
                font-family:'Source Sans Pro',sans-serif;
                font-size:1rem;
            ">{justification}</div>
        </div>
        """
    )


def _render_result_item(
    page: TestPage,
    page_number: int,
    total_pages: int,
    result_stats: dict[str, ItemResult],
) -> None:
    st.progress(page_number / total_pages)
    st.caption(f"Question {page_number} of {total_pages}")

    render_stimulus(page)
    form_key = f"results_{page.item_id}"
    if page.item_type == "DropDown":
        answer_key = "".join(gap.correct_letter for gap in page.gap_option_sets)
        render_dropdown_page(page, form_key, selected_letters=answer_key, disabled=True)
    else:
        answer_key = page.option_set.correct_text if page.option_set else None
        render_mcq_page(page, form_key, selected_answer=answer_key, disabled=True)

    _render_justification(page)

    _render_result_chart(result_stats.get(page.item_id))

    next_page = st.button("Next", type="primary")

    if next_page:
        st.session_state.current_index += 1
        if st.session_state.current_index >= total_pages:
            st.session_state.completed = True
        st.rerun()


def _render_complete() -> None:
    if st.session_state.viewing_results:
        st.title("End of results")
        if st.button("Back to start"):
            st.session_state.started = False
            st.session_state.completed = False
            st.session_state.current_index = 0
            st.session_state.viewing_results = False
            st.rerun()
    else:
        st.title("Thank you")
        st.success("Your responses have been recorded.")
        st.markdown(f"**Session ID:** `{st.session_state.session_id}`")
        st.caption("You may close this window.")


def _load_result_stats_or_stop() -> dict[str, ItemResult]:
    if not RESULTS_PATH.exists():
        st.error("Could not find results.xlsx.")
        st.stop()

    try:
        return _get_result_stats(RESULTS_PATH.stat().st_mtime)
    except Exception as exc:
        st.error(f"Could not load results.xlsx. ({exc})")
        st.stop()


def main() -> None:
    st.set_page_config(page_title="English Placement Pilot", layout="wide")
    _init_state()
    _apply_button_theme()

    pages = _get_pages(CSV_PATH.stat().st_mtime)
    if not pages:
        st.error("No questions found in the CSV file.")
        return

    if not st.session_state.started:
        _render_welcome()
        return

    if st.session_state.completed:
        _render_complete()
        return

    current_index = st.session_state.current_index
    if st.session_state.viewing_results:
        result_stats = _load_result_stats_or_stop()
        _render_result_item(pages[current_index], current_index + 1, len(pages), result_stats)
    else:
        _render_item(pages[current_index], current_index + 1, len(pages))


if __name__ == "__main__":
    main()
