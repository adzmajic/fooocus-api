"""function for call generate worker"""
from typing import List
from fastapi import Response

from fooocusapi.models.common.requests import (
    CommonRequest as Text2ImgRequest
)
from fooocusapi.models.common.response import (
    AsyncJobResponse,
    GeneratedImageResult
)
from fooocusapi.models.common.task import (
    GenerationFinishReason,
    ImageGenerationResult,
    AsyncJobStage,
    TaskType
)
from fooocusapi.utils.api_utils import (
    req_to_params,
    generate_async_output,
    generate_streaming_output,
    generate_image_result_output
)
from fooocusapi.models.requests_v1 import (
    ImgUpscaleOrVaryRequest,
    ImgPromptRequest,
    ImgInpaintOrOutpaintRequest
)
from fooocusapi.models.requests_v2 import (
    ImgInpaintOrOutpaintRequestJson,
    ImgPromptRequestJson,
    ImgUpscaleOrVaryRequestJson
)
from fooocusapi.worker import worker_queue, blocking_get_task_result


def get_task_type(req: Text2ImgRequest) -> TaskType:
    """return task type"""
    if isinstance(req, (ImgUpscaleOrVaryRequest, ImgUpscaleOrVaryRequestJson)):
        return TaskType.img_uov
    if isinstance(req, (ImgPromptRequest, ImgPromptRequestJson)):
        return TaskType.img_prompt
    if isinstance(req, (ImgInpaintOrOutpaintRequest, ImgInpaintOrOutpaintRequestJson)):
        return TaskType.img_inpaint_outpaint
    return TaskType.text_2_img


def call_worker(req: Text2ImgRequest, accept: str) -> Response | AsyncJobResponse | List[GeneratedImageResult]:
    """call generation worker"""
    if accept == 'image/png':
        streaming_output = True
        # image_number auto set to 1 in streaming mode
        req.image_number = 1
    else:
        streaming_output = False

    task_type = get_task_type(req)
    params = req_to_params(req)
    async_task = worker_queue.add_task(task_type, params, req.webhook_url)

    if async_task is None:
        # add to worker queue failed
        failure_results = [
            ImageGenerationResult(
                im=None,
                seed='',
                finish_reason=GenerationFinishReason.queue_is_full
            )]

        if streaming_output:
            return generate_streaming_output(failure_results)
        if req.async_process:
            return AsyncJobResponse(
                job_id='',
                job_type=get_task_type(req),
                job_stage=AsyncJobStage.error,
                job_progress=0,
                job_status=None,
                job_step_preview=None,
                job_result=failure_results)
        return generate_image_result_output(failure_results, False)

    if req.async_process:
        # return async response directly
        return generate_async_output(async_task)

    # blocking get generation result
    results = blocking_get_task_result(async_task.job_id)

    if streaming_output:
        return generate_streaming_output(results)
    return generate_image_result_output(results, req.require_base64)
