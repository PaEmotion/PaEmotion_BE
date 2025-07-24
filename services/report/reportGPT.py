from openai import OpenAI
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()



def report_prompt(period: str, data: str, tone: str,spend_type: str="",  budget_prediction: Optional[float] = None) -> str:
    # period = weekly, monthly 텍스트
    # data = 소비 기록
    # tone = 어조

    # 소비 유형 설명
    type_descriptions = {
    "감정소비형": "특정 감정 상태에서 소비 빈도가 높은 유형입니다.",
    "계획소비형": "사전에 설정한 예산 계획에 기반하여 체계적으로 소비하는 유형입니다.",
    "충동소비형": "소비 패턴의 변동성이 심하며, 감정 상태에 따라 소비 패턴이 크게 달라지는 유형입니다.",
    "관계지향형" : "대인관계 유지 및 강화를 목적으로 지출이 집중되는 유형입니다.",
    "무지출지향형" : "소비를 최소화하며 지출을 극도로 자제하는 유형입니다.",
    "소비성향편중형" : "특정 소비 유형에 소비가 집중된 유형입니다."
    # ... 기타 유형별 설명
    }

    type_descriptions = type_descriptions.get(spend_type)

    # 예측 금액 생성
    prediction_line = (
        f"6. 예측된 다음주 소비 금액은 약 {int(budget_prediction):,}원 임을 출력하세요."
        if budget_prediction not in [None, ""] else ""
    )

    prompts = {
    "weekly": f"""
    1. 지금부터 당신은 영문자를 사용하지 않고 나의 명령을 순서대로 따르세요. 또한, 번호 넘버링도 하지 말며, 조사를 반드시 사용하고 문장이 끝나면 반드시 온점을 붙이세요.
    2. 이번 주의 소비 리포트입니다. 라는 인사 문구를 한 줄 추가하세요.
    3. 이번 주 소비하신 총 금액을 정확하게 숫자와 단위(원)까지 포함하여 제일 먼저 말해주세요.
    4. 감정 별 소비 내역을 반드시 다음의 예시 형식을 따라 한 줄씩 출력하세요. 예: "* 행복 -> 3회, 소비 74,000원"
    5. 가장 많이 느낀 감정을 정확히 한 문장으로 명시하고, 그 감정을 바탕으로 긍정적인 칭찬이나 위로를 짧게 해주세요.
    {prediction_line}

    --- 소비 요약 ---
    {data}
    """
    ,
        "monthly": f"""
    1. 지금부터 당신은 영문자를 사용하지 않습니다. 또한, 번호 넘버링도 하지 말며, 조사를 반드시 사용하고 문장이 끝나면 반드시 온점을 붙이세요.    
    2. 이번 달의 소비 리포트입니다. 라는 인사 문구를 한 줄 추가하세요.
    3. 이번 달의 소비 유형은 {spend_type}입니다. 를 출력하고, 이 유형에 대해 다음 설명을 참고해 한 문장으로 설명해주세요 : {spend_type}.{type_descriptions}
    추가로 이 유형에게 긍정적인 조언이나 충고를 한 문장 해주세요. 부정적인 비판은 반드시 삼가세요.
    4. 그럼 이번 달의 소비 내역을 확인해 볼까요? 같은 류의 화제 전환 말을 한 문장 말하세요.
    5. 이번 달 소비하신 총 금액을 정확하게 숫자와 단위(원)까지 포함하여 말해주세요.
    6. 이번 달의 감정 별 소비 내역을 반드시 한 줄씩 구체적으로 출력하세요. 예: "* 행복 -> 3회, 소비 74,000원"
    7. 이번에는 이라는 연결어를 사용한 뒤 이번 달의 소비 카테고리 랭킹을 순위별로 3위까지만 한 줄씩 출력하세요. 예: "*1위 -> 취미, 2위 -> 배달"
    8. 가장 많이 느낀 감정을 정확히 한 문장으로 명시하고, 그 감정을 바탕으로 긍정적인 칭찬이나 위로를 짧게해 주세요.

    --- 소비 요약 ---
    {data}
    """
    }


    return prompts.get(period, prompts["monthly"]) # 기본값이 daily, 사실 바뀜

import logging
import os
from openai import OpenAI
from typing import Literal



api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

def generate_report(period: Literal["daily", "weekly", "monthly"], data: str, tone: str, spend_type: str ="", budget_prediction=None) -> str:
    prompt_text = report_prompt(period, data, tone, spend_type, budget_prediction)

    messages = [
        {"role": "system", "content": "너는 내 감정 기반 소비 분석 도우미야."},
        {"role": "user", "content": prompt_text}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=600
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"[리포트 생성 실패] {str(e)}"
