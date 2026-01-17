# ui/callbacks/explanation_callbacks_quota.py
#
# Quota-aware callbacks for topic explanation functionality.
# Integrates quota management with explanation generation.
#

import gradio as gr
import logging

from app.auth import SessionManager
from app.services.quota import QuotaExceededError, rate_limiter, input_validator, token_counter
from app.services.explanation import OutputFormatter
from app.services.history import HistoryRepository, HistoryFormatter
from ui.utils.ui_messages import get_history_info_message
from ui.callbacks.auth_callbacks import update_quota_display
from ui.callbacks.shared_services import rag_service

logger = logging.getLogger(__name__)

# Domain service instances
output_formatter = OutputFormatter()
history_repository = HistoryRepository()
history_formatter = HistoryFormatter()


def explain_topic_with_quota_stream(
    topic: str,
    history,
    history_mode: str,
    user_session,
    rag_uploaded_state=None
):
    # Stream explanation with quota management and RAG support
    #
    # Args:
    #     topic: Technical topic(s) to explain (comma-separated for multiple)
    #     history: Current chat history
    #     history_mode: "Aggrega in una sola chat" or "Salva ogni argomento come chat separata"
    #     user_session: UserSession with user_id and quota status
    #     rag_uploaded_state: Unused (kept for compatibility)
    #
    # Yields:
    #     Tuple of (history, output_text, quota_display, history_dropdown_update, delete_dropdown_update)
    
    topic_clean = (topic or "").strip()
    if not topic_clean:
        error_msg = "❌ Please enter at least one technical topic."
        yield history, error_msg, gr.update(), gr.update(), gr.update()
        return
    
    # Extract user_id from session
    user_id = SessionManager.get_user_id_from_session(user_session)
    if not user_id:
        error_msg = "❌ **Authentication Required**\n\nPlease log in with your Hugging Face account to use this service."
        yield history, error_msg, gr.update(), gr.update(), gr.update()
        return
    
    logger.info(f"\n{'='*60}")
    logger.info(f"🎯 Quota-aware explanation request")
    logger.info(f"User: {user_id}")
    logger.info(f"Topic: {topic_clean}")
    
    # Validate topics
    topics = output_formatter.parse_topics(topic_clean)
    aggregate_mode = history_mode == "Aggrega in una sola chat"
    
    # Show initial status
    streaming_badge = "⏳ **Generating explanation...**\n\n"
    yield history, streaming_badge, gr.update(), gr.update(), gr.update()
    
    topic_contents = {}
    topic_modes = {}
    warning_messages = []
    total_input_tokens = 0
    total_output_tokens = 0
    
    try:
        # Process each topic with quota management
        for topic_name in topics:
            logger.info(f"📝 Processing topic: {topic_name}")
            
            # STEP 1: Validate and prepare input
            validation_result = input_validator.validate_and_prepare(
                topic_name,
                user_id=user_id,
                auto_truncate=True
            )
            
            if not validation_result.is_valid:
                raise ValueError(validation_result.error_message)
            
            processed_topic = validation_result.text
            input_tokens = validation_result.token_count
            total_input_tokens += input_tokens
            
            if validation_result.was_truncated and validation_result.warning_message:
                warning_messages.append(validation_result.warning_message)
            
            logger.info(f"✅ Input validated: {input_tokens} tokens")
            
            # STEP 2: Check and reserve quota
            estimated_tokens = rate_limiter.estimate_total_tokens(processed_topic)
            quota_status = rate_limiter.check_and_reserve_quota(user_id, estimated_tokens)
            logger.info(f"✅ Quota check passed: {quota_status.requests_remaining} requests, {quota_status.tokens_remaining} tokens remaining")
            
            # STEP 3: Generate explanation using RAG service (with conditional RAG logic)
            accumulated_for_topic = ""
            mode = None
            
            for accumulated_chunk, chunk_mode in rag_service.explain_topic_stream(processed_topic):
                accumulated_for_topic = accumulated_chunk
                mode = chunk_mode
                
                # Store partial result
                topic_contents[topic_name] = accumulated_for_topic
                topic_modes[topic_name] = mode
                
                # Prepare text for streaming
                if aggregate_mode:
                    accumulated_raw = output_formatter.aggregate_topics_output(topics, topic_contents)
                else:
                    accumulated_raw = f"{topic_name}:\n\n{accumulated_for_topic}"
                
                # Show streaming badge and warnings
                output_text = streaming_badge
                if warning_messages:
                    output_text += "⚠️ **Warnings:**\n"
                    for w in warning_messages:
                        output_text += f"- {w}\n"
                    output_text += "\n"
                output_text += accumulated_raw
                
                yield history, output_text, gr.update(), gr.update(), gr.update()
            
            # STEP 4: Count output tokens and consume quota
            output_tokens = token_counter.count_tokens(accumulated_for_topic)
            total_output_tokens += output_tokens
            
            rag_used = (mode == "rag")
            
            rate_limiter.consume_quota(
                user_id=user_id,
                topic=processed_topic,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                rag_used=rag_used,
                success=True
            )
            
            logger.info(f"✅ Quota consumed: +{input_tokens + output_tokens} tokens (input: {input_tokens}, output: {output_tokens})")
            
            # Sanitize final output for this topic
            topic_contents[topic_name] = output_formatter.sanitize_output(accumulated_for_topic)
            logger.info(f"✅ Topic completed: {topic_name}")
    
    except QuotaExceededError as e:
        # Quota exceeded error
        error_msg = f"🚫 **Quota Exceeded**\n\n{str(e)}\n\n"
        error_msg += "Your daily quota has been exhausted. Please wait for the reset or contact support."
        
        # Update quota display
        updated_quota_display = update_quota_display(user_session)
        
        logger.error(f"❌ Quota exceeded for user {user_id}: {str(e)}")
        yield history, error_msg, updated_quota_display, gr.update(), gr.update()
        return
    
    except ValueError as e:
        # Validation error (input too long, etc.)
        error_msg = f"❌ **Invalid Input**\n\n{str(e)}"
        logger.error(f"❌ Validation error for user {user_id}: {str(e)}")
        yield history, error_msg, gr.update(), gr.update(), gr.update()
        return
    
    except Exception as e:
        # Generic error
        error_msg = f"❌ **Error**\n\nAn error occurred while generating the explanation:\n\n{str(e)}"
        logger.error(f"❌ Unexpected error for user {user_id}: {str(e)}", exc_info=True)
        yield history, error_msg, gr.update(), gr.update(), gr.update()
        return
    
    # Final aggregation
    final_text = output_formatter.aggregate_topics_output(topics, topic_contents)
    
    # Add badge for knowledge source (RAG/Generic/Mixed)
    used_rag = any(mode == "rag" for mode in topic_modes.values())
    used_generic = any(mode == "generic" for mode in topic_modes.values())
    
    if used_rag and not used_generic:
        badge = "🧠 **Answer generated using your documents**\n\n"
    elif used_generic and not used_rag:
        badge = "🌐 **Answer generated using general knowledge**\n\n"
    else:
        badge = "🔀 **Answer generated using both documents and general knowledge**\n\n"
    
    # Add warnings if any
    if warning_messages:
        badge += "⚠️ **Warnings:**\n"
        for w in warning_messages:
            badge += f"- {w}\n"
        badge += "\n"
    
    # Add quota info
    badge += f"📊 **Tokens used:** {total_input_tokens + total_output_tokens} (input: {total_input_tokens}, output: {total_output_tokens})\n\n"
    
    final_output = badge + final_text
    
    # Update history
    if aggregate_mode:
        # Aggregate mode: save all topics in one entry, separated by comma
        history = history_repository.add_to_history(", ".join(topics), final_output, history)
    else:
        # Separate mode: save each topic as individual entry
        for t in topics:
            individual_output = badge + topic_contents[t]
            history = history_repository.add_to_history(t, individual_output, history)
    
    # Update dropdowns
    radio_choices, _ = history_formatter.create_history_choices(history)
    delete_choices = history_formatter.create_delete_choices(history)
    info_msg = get_history_info_message(len(history))
    
    # Update quota display
    updated_quota_display = update_quota_display(user_session)
    
    logger.info(f"✅ Explanation completed successfully")
    logger.info(f"{'='*60}\n")
    
    yield (
        history,
        final_output,
        updated_quota_display,
        gr.update(choices=radio_choices, info=info_msg),
        gr.update(choices=delete_choices)
    )

