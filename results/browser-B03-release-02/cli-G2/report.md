# CEAV-M1 — Phân tích rbts

Trạng thái candidate: **exact_pure_equilibrium**. Max regret: 0.

Accuracy: 7/10; false approval P(D=1|Y=0): 3/10; giải ngân sai kỳ vọng: 3/20.

Thực chi reward: 6; maximum reward: 6; budget: 6.

Candidate payoff sử dụng candidate thật; best response và witness nằm trong best_responses.json. Witness giữ prediction của peer tại run gốc; dựng lại Bayesian predictions của một profile mới có thể thay đổi payoff.

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

Candidate effort/report profile:

```json
{
  "0": [
    "L0",
    "L0",
    "L0"
  ],
  "1": [
    "L1",
    "L1",
    "L1"
  ]
}
```

M1: một claim, ba Judge; effort sau public Z; không stake/slashing, không ground-truth reward; chỉ cân bằng thuần, không chứng nhận mixed/coalition hoặc equilibrium selection. Đơn vị nghiên cứu chuẩn hóa, không phải tiền thực. Cân bằng không effort như all-Z có thể cùng tồn tại với high-effort; tăng lambda không tự loại bỏ cân bằng đạt score maximum.
