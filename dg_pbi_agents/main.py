import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# from agents.gatekeeper1 import check_if_business_question
# fro s2 import select_dataset
#
#
# def main(user_input: str):
#     #1·查看置信度,判断用户问题是否属于业务范畴
#     if_business, confidence = check_if_business_question(user_input)
#     if not if_business or confidence < 0.6:
#         return "该问题不是业务数据相关的问题。"
#     else:
#         print(f'用户提问:{user_input} 与业务相关。其置信度为{confidence}!')
#         #2·根据用户提问定位到可能找到答案的dataset
#         dataset_id, dataset_name, dataset_description = select_dataset(user_input)
#         print(f'根据用户的提问可能在{dataset_name}中找到答案!"\n"{dataset_description}')
#         #3·查询根据dataset_id定位到metadata (function call)
#         #4·结合user_input + metadata作为提示词，识别问题中的关键实体,定位到解决用户问题需要查询dataset中的哪些table和cloumn,如果有filter条件也要选出来
#         #5·结合user_input + 第四步输出的结构化数据(eg:{})为提示词生成相关dax公式
#         #6·连接power bi client执行dax,返还结果(function call)
#         #7·llm校验结果是否可以输出,如果执行报错或者查询结果比较离谱，llm会判断是dax生成有错还是dataset和metadata选取有误进行replan操作

import asyncio
from typing import Optional
from agents.gatekeeper1 import BusinessClassifier
from agents.match_ds2 import DatasetMatcher
from dg_pbi_agents.services.metadata_service import MetadataService
from schemas.base import (
    BusinessCheckResult,
    DatasetInfo,
    DatasetMetadata,
    QueryPlan,
    DAXRequest,
    DAXResponse,
    ExecutionResult,
    ValidationResult
)
from agents.query_analyzner import QueryAnalyzer

class PipelineRunner:
    def __init__(self):
        self.metadata_service = MetadataService(json_file_path = r'C:\Users\sean\PycharmProjects\ai-cookbook\dg_pbi_agents\services\metadata.json')
        # self.pbi_client = PBIClient("https://api.powerbi.com")
        self.max_retries = 3
        self.BusinessClassifier =BusinessClassifier()
        self.dataset_matcher = DatasetMatcher()

   
    async def run_pipeline(self, user_input: str) -> Optional[dict]:
        # 步骤1：业务检查
        is_business_question = await self._check_business_relevance(user_input)
        print(f"步骤1结果: {is_business_question}")
        if not is_business_question.is_business==True:
            print(f"用户提问: {user_input} 与业务相关性检查未通过，原因是: {is_business_question.response}")
            return None
        print(f"用户提问: {user_input} 与业务相关性检查通过，原因是: {is_business_question.response}")

  
        # 步骤2：选择数据集
        # 步骤3：获取元数据
        _get_metadata = await self._get_metadata(user_input)
        if not _get_metadata:
            print(f"未找到与用户提问相关的数据集元数据，问题可能不在任何已知数据集中。")
            return None
        # 步骤4：生成查询计划
        query_plan = await self._generate_query_plan(user_input, _get_metadata)
        a=1
        print(f"步骤4结果: {query_plan}")

        return query_plan

        # retry_count = 0
        # while retry_count < self.max_retries:
        #     # 步骤4：生成查询计划
        #     query_plan = await QueryAnalyzer().analyze(userinput, metadata)
        #
        #     # 步骤5：生成DAX
        #     dax_request = DAXRequest(question=user_input, query_plan=query_plan)
        #     dax_response = await DAXGenerator().generate(dax_request)
        #
        #     # 步骤6：执行查询
        #     exec_result = await self.pbi_client.execute_dax(
        #         dataset_info.id,
        #         dax_response.expression
        #     )
        #
        #     # 步骤7：验证结果
        #     validation = await ResultValidator().validate(exec_result, {
        #         "question": user_input,
        #         "dax_expression": dax_response.expression
        #     })
        #
        #     if validation.is_valid:
        #         return exec_result.data
        #     else:
        #         retry_count += 1
        #         print(f"验证失败：{validation.feedback}，开始重试 ({retry_count}/{self.max_retries})")
        #
        # return None

    async def _check_business_relevance(self, question: str) -> BusinessCheckResult:
        return await self.BusinessClassifier.check(question)

    async def _chose_dataset(self, question: str) -> DatasetInfo:
        # 调用dataset_matcher的实现
        return await self.dataset_matcher.match(question) 
    
    async def _get_metadata(self, question: str) -> DatasetMetadata:
        # 调用metadata_service的实现
        dataset_info = await self._chose_dataset(question)
        return await self.metadata_service.get_metadata(dataset_info.dataset_id) if dataset_info.dataset_id else None
    
    async def _generate_query_plan(self, question: str, metadata: DatasetMetadata) -> QueryPlan:
        """生成查询计划"""
        return await QueryAnalyzer().analyze(question, metadata)







if __name__ == '__main__':
    user_input = '我想查看近两天开了多少bug,其中p1的bug占总数比'
    runner = PipelineRunner()

    async def main():
        await runner.run_pipeline(user_input)

    asyncio.run(main())