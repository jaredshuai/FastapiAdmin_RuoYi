from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, Query
from fastapi.responses import JSONResponse

from app.common.response import ResponseSchema, SuccessResponse
from app.core.base_schema import AuthSchema, PageResultSchema
from app.core.dependencies import AuthPermission
from app.core.router_class import OperationLogRoute

from .schema import (
    InvoiceApplySchema,
    InvoiceIssueSchema,
    InvoiceOutSchema,
    InvoiceQueryParam,
    InvoiceVoidSchema,
)
from .service import InvoicePlatformService, InvoiceTenantService

TenantInvoiceRouter = APIRouter(prefix="/tenant/invoice", route_class=OperationLogRoute, tags=["平台管理", "发票管理"])

@TenantInvoiceRouter.post("/apply", summary="申请开票", response_model=ResponseSchema[InvoiceOutSchema])
async def invoice_apply_controller(
    data: Annotated[InvoiceApplySchema, Body()],
    auth: Annotated[AuthSchema, Depends(AuthPermission(["*:*:*"]))],
) -> JSONResponse:
    result = await InvoiceTenantService.apply(auth, data, auth.tenant_id)
    return SuccessResponse(data=result, msg="发票申请成功")

@TenantInvoiceRouter.get("/list", summary="我的发票列表", response_model=ResponseSchema[PageResultSchema[InvoiceOutSchema]])
async def invoice_list_my_controller(
    auth: Annotated[AuthSchema, Depends(AuthPermission(["*:*:*"]))],
    invoice_type: Annotated[str | None, Query()] = None,
    status: Annotated[int | None, Query()] = None,
    page_no: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 10,
) -> JSONResponse:
    result = await InvoiceTenantService.list_my(
        auth,
        auth.tenant_id,
        InvoiceQueryParam(invoice_type=invoice_type, status=status, page_no=page_no, page_size=page_size),
    )
    return SuccessResponse(data=result, msg="查询成功")

@TenantInvoiceRouter.get("/{id}/download", summary="下载发票PDF", response_model=ResponseSchema[dict])
async def invoice_download_controller(
    id: Annotated[int, Path(ge=1)],
    auth: Annotated[AuthSchema, Depends(AuthPermission(["*:*:*"]))],
) -> JSONResponse:
    pdf_url = await InvoiceTenantService.download(auth, id, auth.tenant_id)
    return SuccessResponse(msg="下载地址", data={"pdf_url": pdf_url})

PlatformInvoiceRouter = APIRouter(prefix="/invoice", route_class=OperationLogRoute, tags=["平台管理", "发票管理"])

@PlatformInvoiceRouter.get("/list", summary="全部发票列表", response_model=ResponseSchema[PageResultSchema[InvoiceOutSchema]])
async def invoice_list_all_controller(
    auth: Annotated[AuthSchema, Depends(AuthPermission(["*:*:*"]))],
    invoice_type: Annotated[str | None, Query()] = None,
    status: Annotated[int | None, Query()] = None,
    tenant_id: Annotated[int | None, Query()] = None,
    page_no: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 10,
) -> JSONResponse:
    result = await InvoicePlatformService.list_all(
        auth,
        InvoiceQueryParam(invoice_type=invoice_type, status=status, tenant_id=tenant_id, page_no=page_no, page_size=page_size),
    )
    return SuccessResponse(data=result, msg="查询成功")

@PlatformInvoiceRouter.put("/issue/{id}", summary="开具发票", response_model=ResponseSchema[InvoiceOutSchema])
async def invoice_issue_controller(
    id: Annotated[int, Path(ge=1)],
    data: Annotated[InvoiceIssueSchema, Body()],
    auth: Annotated[AuthSchema, Depends(AuthPermission(["*:*:*"]))],
) -> JSONResponse:
    result = await InvoicePlatformService.issue(
        auth,
        id,
        data.pdf_url or "",
        data.api_response or "",
    )
    return SuccessResponse(data=result, msg="发票开具成功")

@PlatformInvoiceRouter.put("/void/{id}", summary="作废发票", response_model=ResponseSchema[InvoiceOutSchema])
async def invoice_void_controller(
    id: Annotated[int, Path(ge=1)],
    auth: Annotated[AuthSchema, Depends(AuthPermission(["*:*:*"]))],
    data: Annotated[InvoiceVoidSchema, Body()] = InvoiceVoidSchema(),
) -> JSONResponse:
    result = await InvoicePlatformService.void(auth, id, data)
    return SuccessResponse(data=result, msg="发票已作废")
