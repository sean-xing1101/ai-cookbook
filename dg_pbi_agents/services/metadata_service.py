import asyncio
import json
import math
from typing import Optional

from dg_pbi_agents.schemas.base import DatasetMetadata

class MetadataService:
    def __init__(self, json_file_path: str):
        self.json_file_path = json_file_path

    def _load_dataset_from_json(self, dataset_id: str) -> Optional[DatasetMetadata]:
        with open(self.json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        for dataset in data.get('datasets', []):
            if dataset['dataset_id'] == dataset_id:
                # 处理 NaN 值，将其转换为空字符串
                def sanitize(value):
                    if isinstance(value, float) and math.isnan(value):
                        return ""
                    elif isinstance(value, list):
                        return [sanitize(item) for item in value]
                    elif isinstance(value, dict):
                        return {k: sanitize(v) for k, v in value.items()}
                    return value

                sanitized_dataset = {
                    key: sanitize(value) for key, value in dataset.items()
                }
                return DatasetMetadata(**sanitized_dataset)  # 转换为 DatasetMetadata 对象

        print('metadata do not have dataset id: {}'.format(dataset_id))
        return None

    async def get_metadata(self, dataset_id: str) -> DatasetMetadata:
        """获取数据集元数据"""
        meta_json = self._load_dataset_from_json(dataset_id)
        if meta_json is None:
            raise ValueError(f"Dataset with ID {dataset_id} not found in metadata.")
        return meta_json

# 示例调用
async def main():
    a = MetadataService(json_file_path=r'C:\Users\sean\PycharmProjects\ai-cookbook\dg_pbi_agents\services\metadata.json')
    try:
        res = await a.get_metadata(dataset_id='07942bb8-483f-48d0-82c1-72bafe83685e')
        print('获取到的元数据:', res)
    except ValueError as e:
        print(e)

# 运行异步主函数
# if __name__ == "__main__":
#     asyncio.run(main())