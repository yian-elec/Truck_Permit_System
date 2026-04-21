"""
seed_loader.py - Seed 資料載入工具
彈性的 JSON 文件載入工具，由各 context 的 infra seed 文件呼叫
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


def load_seed_data(table_name: str, seed_dir: str) -> List[Dict[str, Any]]:
    """
    載入指定表的 seed 資料
    
    Args:
        table_name: 表名（對應 JSON 文件名）
        seed_dir: seed 資料夾路徑
        
    Returns:
        List[Dict[str, Any]]: seed 資料列表
    """
    seed_path = Path(seed_dir)
    json_file = seed_path / f"{table_name}.json"
    
    if not json_file.exists():
        logger.warning(f"Seed file not found: {json_file}")
        return []
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 確保返回的是列表格式
        if isinstance(data, list):
            seed_data = data
        elif isinstance(data, dict):
            # 如果是字典，可能包含 metadata，嘗試獲取 'data' 欄位
            if 'data' in data and isinstance(data['data'], list):
                seed_data = data['data']
            else:
                # 如果沒有 'data' 欄位，將整個字典包裝成列表
                seed_data = [data]
        else:
            logger.error(f"Invalid seed data format in {json_file}")
            return []
        
        logger.info(f"Loaded {len(seed_data)} records from {json_file}")
        return seed_data
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {json_file}: {e}")
        return []
    except Exception as e:
        logger.error(f"Error loading seed data from {json_file}: {e}")
        return []


def get_all_seed_files(seed_dir: str) -> List[Path]:
    """
    獲取指定目錄下所有 seed JSON 文件
    
    Args:
        seed_dir: seed 資料夾路徑
        
    Returns:
        List[Path]: 所有 JSON 文件的路徑列表
    """
    seed_path = Path(seed_dir)
    
    if not seed_path.exists():
        logger.warning(f"Seed directory does not exist: {seed_path}")
        return []
    
    json_files = list(seed_path.glob("*.json"))
    logger.info(f"Found {len(json_files)} seed files in {seed_path}")
    
    return json_files


def get_available_tables(seed_dir: str) -> List[str]:
    """
    獲取指定目錄下所有可用的表名
    
    Args:
        seed_dir: seed 資料夾路徑
        
    Returns:
        List[str]: 表名列表
    """
    json_files = get_all_seed_files(seed_dir)
    return [f.stem for f in json_files]


def load_all_seed_data(seed_dir: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    載入指定目錄下所有 seed 資料
    
    Args:
        seed_dir: seed 資料夾路徑
        
    Returns:
        Dict[str, List[Dict[str, Any]]]: 以表名為 key 的 seed 資料字典
    """
    all_seed_data = {}
    json_files = get_all_seed_files(seed_dir)
    
    for json_file in json_files:
        table_name = json_file.stem  # 獲取文件名（不含副檔名）
        seed_data = load_seed_data(table_name, seed_dir)
        
        if seed_data:
            all_seed_data[table_name] = seed_data
            logger.info(f"Loaded seed data for table '{table_name}': {len(seed_data)} records")
        else:
            logger.warning(f"No seed data loaded for table '{table_name}'")
    
    return all_seed_data


def validate_seed_data(table_name: str, seed_dir: str, required_fields: List[str] = None) -> bool:
    """
    驗證指定表的 seed 資料格式
    
    Args:
        table_name: 表名
        seed_dir: seed 資料夾路徑
        required_fields: 必填欄位列表
        
    Returns:
        bool: 驗證是否通過
    """
    seed_data = load_seed_data(table_name, seed_dir)
    
    if not seed_data:
        logger.error(f"No seed data found for table '{table_name}'")
        return False
    
    if required_fields:
        for i, record in enumerate(seed_data):
            for field in required_fields:
                if field not in record:
                    logger.error(f"Missing required field '{field}' in record {i} of table '{table_name}'")
                    return False
    
    logger.info(f"Seed data validation passed for table '{table_name}'")
    return True


def ensure_seed_dir(seed_dir: str) -> bool:
    """
    確保 seed 資料夾存在
    
    Args:
        seed_dir: seed 資料夾路徑
        
    Returns:
        bool: 是否成功創建或已存在
    """
    try:
        seed_path = Path(seed_dir)
        if not seed_path.exists():
            seed_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created seed directory: {seed_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to create seed directory {seed_dir}: {e}")
        return False
