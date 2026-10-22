# CEAV-M1 — Tìm cân bằng thuần

Đã kiểm tra 432 candidates; số cân bằng theo Z: {'0': 10, '1': 10}; tổ hợp đầy đủ: 100.

Cartesian product of retained z=0 and z=1 branch IDs; choose both branches before analyzing metrics.

Miền tham số: 0 < pi,a,b < 1; costs, f, lambda, F, B, V, operating_cost >= 0.

Cấu hình thực tế của run:

```json
{
  "a": "7/10",
  "b": "4/5",
  "costs": [
    "1/20",
    "1/20",
    "1/20"
  ],
  "f": "0",
  "fixed_reward": "2",
  "lambda": "1",
  "model_version": "ceav-m1-v1.0",
  "operating_cost": "0",
  "payout_value": "1",
  "pi": "1/2",
  "reward_budget": "6"
}
```

M1: một claim, ba Judge; effort sau public Z; không stake/slashing, không ground-truth reward; chỉ cân bằng thuần, không chứng nhận mixed/coalition hoặc equilibrium selection. Đơn vị nghiên cứu chuẩn hóa, không phải tiền thực. Cân bằng không effort như all-Z có thể cùng tồn tại với high-effort; tăng lambda không tự loại bỏ cân bằng đạt score maximum.
