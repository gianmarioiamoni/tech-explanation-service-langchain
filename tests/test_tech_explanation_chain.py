# tests/test_tech_explanation_chain
#
# Test for the LCEL tech explanation chain


from app.chains.tech_explanation_chain import tech_explanation_chain

# --- Test TechExplanationChain ---
def test_tech_explanation_chain_returns_string():
    result = tech_explanation_chain.invoke(
        {"topic": "Dependency Injection"}
    )

    assert isinstance(result, str)
    assert len(result) > 0




