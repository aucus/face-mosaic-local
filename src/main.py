#!/usr/bin/env python3
"""
Face Mosaic Local - CLI 진입점

로컬 기반 얼굴 모자이크 처리 프로그램의 메인 진입점입니다.
"""

import argparse
import sys
from pathlib import Path

from .processor import FaceMosaicProcessor
from .utils import setup_logger


def parse_args() -> argparse.Namespace:
    """명령줄 인자를 파싱합니다."""
    parser = argparse.ArgumentParser(
        description="Face Mosaic Local - 로컬 기반 얼굴 모자이크 처리 프로그램",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  # 기본 사용 (DNN 감지기, 모자이크)
  python -m src.main --input ./photos --output ./output

  # Haar Cascade 감지기 사용
  python -m src.main --input ./photos --output ./output --detector haar

  # 블러 효과 사용
  python -m src.main --input ./photos --output ./output --method blur

  # 모자이크 크기 조절
  python -m src.main --input ./photos --output ./output --mosaic-size 20

  # 신뢰도 임계값 조절
  python -m src.main --input ./photos --output ./output --confidence 0.7
        """
    )
    
    # 필수 인자
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="입력 폴더 경로"
    )
    
    # 선택 인자
    parser.add_argument(
        "--output",
        type=str,
        default="./output",
        help="출력 폴더 경로 (기본값: ./output)"
    )
    
    parser.add_argument(
        "--detector",
        type=str,
        choices=["haar", "dnn"],
        default="dnn",
        help="얼굴 감지기 타입 (기본값: dnn)"
    )
    
    parser.add_argument(
        "--mosaic-size",
        type=int,
        default=10,
        help="모자이크 블록 크기 (작을수록 블록이 큼, 기본값: 10)"
    )
    
    parser.add_argument(
        "--method",
        type=str,
        choices=["mosaic", "blur"],
        default="mosaic",
        help="처리 방법 (기본값: mosaic)"
    )
    
    parser.add_argument(
        "--confidence",
        type=float,
        default=0.5,
        help="DNN 감지기 신뢰도 임계값 (0.0 ~ 1.0, 기본값: 0.5)"
    )
    
    parser.add_argument(
        "--blur-kernel-size",
        type=int,
        default=51,
        help="블러 커널 크기 (기본값: 51, 홀수만 가능)"
    )
    
    parser.add_argument(
        "--quality",
        type=int,
        default=95,
        help="저장 품질 (1-100, 기본값: 95)"
    )
    
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="하위 폴더까지 재귀적으로 처리"
    )
    
    parser.add_argument(
        "--log-file",
        type=str,
        default=None,
        help="로그 파일 경로 (지정하지 않으면 파일 로깅 없음)"
    )
    
    parser.add_argument(
        "--logo",
        type=str,
        default=None,
        help="로고 파일 경로 (PNG, JPG, JPEG 지원)"
    )
    
    parser.add_argument(
        "--logo-size",
        type=float,
        default=0.1,
        help="로고 크기 비율 (0.0 ~ 1.0, 기본값: 0.1)"
    )
    
    parser.add_argument(
        "--logo-margin",
        type=int,
        default=20,
        help="로고 여백 (픽셀, 기본값: 20)"
    )
    
    parser.add_argument(
        "--logo-opacity",
        type=float,
        default=1.0,
        help="로고 투명도 (0.0 ~ 1.0, 기본값: 1.0)"
    )
    
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    """인자 유효성을 검사합니다."""
    # 입력 폴더 확인
    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"입력 폴더를 찾을 수 없습니다: {args.input}")
    if not input_path.is_dir():
        raise ValueError(f"입력 경로가 폴더가 아닙니다: {args.input}")
    
    # 출력 폴더 생성 (없으면)
    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 품질 범위 확인
    if not (1 <= args.quality <= 100):
        raise ValueError(f"품질은 1-100 사이여야 합니다: {args.quality}")
    
    # 모자이크 크기 확인
    if args.mosaic_size < 1:
        raise ValueError(f"모자이크 크기는 1 이상이어야 합니다: {args.mosaic_size}")
    
    # 블러 커널 크기 확인
    if args.blur_kernel_size < 1:
        raise ValueError(f"블러 커널 크기는 1 이상이어야 합니다: {args.blur_kernel_size}")
    
    # 신뢰도 범위 확인
    if not (0.0 <= args.confidence <= 1.0):
        raise ValueError(f"신뢰도는 0.0-1.0 사이여야 합니다: {args.confidence}")
    
    # 로고 옵션 확인
    if args.logo:
        logo_path = Path(args.logo)
        if not logo_path.exists():
            raise FileNotFoundError(f"로고 파일을 찾을 수 없습니다: {args.logo}")
        if not logo_path.is_file():
            raise ValueError(f"로고 경로가 파일이 아닙니다: {args.logo}")
        
        # 로고 크기 비율 확인
        if not (0.0 < args.logo_size <= 1.0):
            raise ValueError(f"로고 크기는 0.0-1.0 사이여야 합니다: {args.logo_size}")
        
        # 로고 여백 확인
        if args.logo_margin < 0:
            raise ValueError(f"로고 여백은 0 이상이어야 합니다: {args.logo_margin}")
        
        # 로고 투명도 확인
        if not (0.0 <= args.logo_opacity <= 1.0):
            raise ValueError(f"로고 투명도는 0.0-1.0 사이여야 합니다: {args.logo_opacity}")


def main() -> int:
    """메인 함수."""
    try:
        # 인자 파싱
        args = parse_args()
        
        # 인자 유효성 검사
        validate_args(args)
        
        # 로거 설정
        logger = setup_logger("face_mosaic", log_file=args.log_file)
        
        logger.info("Face Mosaic Local 시작")
        logger.info(f"입력 폴더: {args.input}")
        logger.info(f"출력 폴더: {args.output}")
        logger.info(f"감지기: {args.detector}")
        logger.info(f"처리 방법: {args.method}")
        if args.logo:
            logger.info(f"로고 파일: {args.logo}")
            logger.info(f"로고 크기: {args.logo_size}")
            logger.info(f"로고 여백: {args.logo_margin}px")
            logger.info(f"로고 투명도: {args.logo_opacity}")
        
        # 감지기 파라미터 설정
        detector_kwargs = {}
        if args.detector == "dnn":
            detector_kwargs["confidence_threshold"] = args.confidence
        
        # 프로세서 생성
        processor = FaceMosaicProcessor(
            detector_type=args.detector,
            detector_kwargs=detector_kwargs,
            method=args.method,
            mosaic_size=args.mosaic_size,
            blur_kernel_size=args.blur_kernel_size,
            quality=args.quality,
            logo_path=args.logo,
            logo_scale=args.logo_size,
            logo_margin=args.logo_margin,
            logo_opacity=args.logo_opacity
        )
        
        # 폴더 처리
        stats = processor.process_folder(
            input_dir=args.input,
            output_dir=args.output,
            recursive=args.recursive
        )
        
        # 성공 여부 반환
        if stats["failed"] > 0:
            logger.warning(f"{stats['failed']}개 이미지 처리 실패")
            return 1
        
        logger.info("모든 이미지 처리 완료")
        return 0
    
    except KeyboardInterrupt:
        print("\n사용자에 의해 중단되었습니다.")
        return 130
    
    except Exception as e:
        print(f"오류 발생: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
