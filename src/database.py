# -*- coding: UTF-8 -*-

import json
import sqlite3

import bcrypt
from loguru import logger


class Database:
    def __init__(self, db_path="cache/fund_data.db"):
        self.db_path = db_path
        self.init_database()

    def get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 返回字典格式
        return conn

    def init_database(self):
        """初始化数据库表"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # 创建用户表
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS users
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           username
                           TEXT
                           UNIQUE
                           NOT
                           NULL,
                           password_hash
                           TEXT
                           NOT
                           NULL,
                           created_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP
                       )
                       ''')

        # 创建用户基金表
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS user_funds
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           user_id
                           INTEGER
                           NOT
                           NULL,
                           fund_code
                           TEXT
                           NOT
                           NULL,
                           fund_key
                           TEXT
                           NOT
                           NULL,
                           fund_name
                           TEXT
                           NOT
                           NULL,
                           is_hold
                           BOOLEAN
                           DEFAULT
                           0,
                           shares
                           REAL
                           DEFAULT
                           0,
                           sectors
                           TEXT,
                           FOREIGN
                           KEY
                       (
                           user_id
                       ) REFERENCES users
                       (
                           id
                       ) ON DELETE CASCADE,
                           UNIQUE
                       (
                           user_id,
                           fund_code
                       )
                           )
                       ''')

        conn.commit()
        conn.close()
        logger.debug("Database initialized successfully")

    # ==================== User Operations ====================

    def create_user(self, username, password):
        """创建新用户

        Args:
            username: 用户名
            password: 明文密码

        Returns:
            (success: bool, message: str, user_id: int or None)
        """
        try:
            # 检查用户名是否已存在
            if self.get_user_by_username(username):
                return False, "用户名已存在", None

            # 生成密码哈希
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12))

            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO users (username, password_hash) VALUES (?, ?)',
                (username, password_hash)
            )
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()

            logger.info(f"User created successfully: {username} (ID: {user_id})")
            return True, "注册成功", user_id

        except Exception as e:
            logger.error(f"Failed to create user {username}: {e}")
            return False, f"注册失败: {str(e)}", None

    def get_user_by_username(self, username):
        """根据用户名获取用户信息

        Returns:
            dict or None
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            row = cursor.fetchone()
            conn.close()

            if row:
                return dict(row)
            return None

        except Exception as e:
            logger.error(f"Failed to get user {username}: {e}")
            return None

    def verify_password(self, username, password):
        """验证用户密码

        Returns:
            (success: bool, user_id: int or None)
        """
        try:
            user = self.get_user_by_username(username)
            if not user:
                return False, None

            password_hash = user['password_hash']
            if isinstance(password_hash, str):
                password_hash = password_hash.encode('utf-8')

            if bcrypt.checkpw(password.encode('utf-8'), password_hash):
                return True, user['id']
            else:
                return False, None

        except Exception as e:
            logger.error(f"Failed to verify password for {username}: {e}")
            return False, None

    # ==================== Fund Operations ====================

    def get_user_funds(self, user_id):
        """获取用户的所有基金数据

        Returns:
            dict: 格式与 fund_map.json 相同
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM user_funds WHERE user_id = ?', (user_id,))
            rows = cursor.fetchall()
            conn.close()

            fund_map = {}
            for row in rows:
                fund_code = row['fund_code']
                sectors = json.loads(row['sectors']) if row['sectors'] else []

                fund_map[fund_code] = {
                    'fund_key': row['fund_key'],
                    'fund_name': row['fund_name'],
                    'is_hold': bool(row['is_hold']),
                    'shares': float(row['shares']) if row['shares'] else 0,
                }

                if sectors:
                    fund_map[fund_code]['sectors'] = sectors

            return fund_map

        except Exception as e:
            logger.error(f"Failed to get funds for user {user_id}: {e}")
            return {}

    def save_user_funds(self, user_id, fund_map):
        """保存用户的所有基金数据（完全替换）

        Args:
            user_id: 用户ID
            fund_map: dict, 格式与 fund_map.json 相同
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # 删除用户现有的所有基金数据
            cursor.execute('DELETE FROM user_funds WHERE user_id = ?', (user_id,))

            # 插入新的基金数据
            for fund_code, fund_data in fund_map.items():
                sectors_json = json.dumps(fund_data.get('sectors', []), ensure_ascii=False)

                cursor.execute('''
                               INSERT INTO user_funds
                                   (user_id, fund_code, fund_key, fund_name, is_hold, shares, sectors)
                               VALUES (?, ?, ?, ?, ?, ?, ?)
                               ''', (
                                   user_id,
                                   fund_code,
                                   fund_data['fund_key'],
                                   fund_data['fund_name'],
                                   1 if fund_data.get('is_hold', False) else 0,
                                   fund_data.get('shares', 0),
                                   sectors_json
                               ))

            conn.commit()
            conn.close()
            logger.debug(f"Saved {len(fund_map)} funds for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to save funds for user {user_id}: {e}")
            return False

    def update_fund_shares(self, user_id, fund_code, shares):
        """更新基金持仓份额

        Args:
            user_id: 用户ID
            fund_code: 基金代码
            shares: 份额数量
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                           UPDATE user_funds
                           SET shares = ?
                           WHERE user_id = ?
                             AND fund_code = ?
                           ''', (shares, user_id, fund_code))

            conn.commit()
            affected_rows = cursor.rowcount
            conn.close()

            if affected_rows > 0:
                logger.debug(f"Updated shares for user {user_id}, fund {fund_code}: {shares}")
                return True
            else:
                logger.warning(f"No fund found to update: user {user_id}, fund {fund_code}")
                return False

        except Exception as e:
            logger.error(f"Failed to update shares: {e}")
            return False

    def add_fund(self, user_id, fund_code, fund_key, fund_name):
        """添加基金到用户列表

        Returns:
            bool: 是否成功
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO user_funds
                (user_id, fund_code, fund_key, fund_name, is_hold, shares, sectors)
                VALUES (?, ?, ?, ?, 0, 0, '[]')
            ''', (user_id, fund_code, fund_key, fund_name))

            conn.commit()
            conn.close()
            logger.debug(f"Added fund {fund_code} for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to add fund: {e}")
            return False

    def delete_fund(self, user_id, fund_code):
        """删除用户的基金

        Returns:
            bool: 是否成功
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                           DELETE
                           FROM user_funds
                           WHERE user_id = ?
                             AND fund_code = ?
                           ''', (user_id, fund_code))

            conn.commit()
            affected_rows = cursor.rowcount
            conn.close()

            if affected_rows > 0:
                logger.debug(f"Deleted fund {fund_code} for user {user_id}")
                return True
            else:
                logger.warning(f"No fund found to delete: user {user_id}, fund {fund_code}")
                return False

        except Exception as e:
            logger.error(f"Failed to delete fund: {e}")
            return False
