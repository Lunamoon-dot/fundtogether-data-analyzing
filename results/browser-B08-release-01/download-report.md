# CEAV-M1 — Phân tích rbts

Trạng thái candidate: **not_equilibrium**. Max regret: 1726933/1734605000.

Accuracy: 112/125; false approval P(D=1|Y=0): 13/125; giải ngân sai kỳ vọng: 13/250.

Thực chi reward: 501650643/216825625; maximum reward: 3; budget: 6.

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
  "lambda": "1/2",
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
    "H01",
    "H01",
    "H01"
  ],
  "1": [
    "H01",
    "H01",
    "H01"
  ]
}
```

M1: một claim, ba Judge; effort sau public Z; không stake/slashing, không ground-truth reward; chỉ cân bằng thuần, không chứng nhận mixed/coalition hoặc equilibrium selection. Đơn vị nghiên cứu chuẩn hóa, không phải tiền thực. Cân bằng không effort như all-Z có thể cùng tồn tại với high-effort; tăng lambda không tự loại bỏ cân bằng đạt score maximum.
