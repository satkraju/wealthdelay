import { getBrand, type Brand } from "../theme";

export const Watermark: React.FC<{ brand?: Brand }> = ({ brand }) => {
  const b = brand ?? getBrand("lor");
  return (
    <div
      style={{
        position: "absolute",
        top: 28,
        right: 36,
        fontFamily: b.font,
        fontSize: 18,
        fontWeight: 600,
        letterSpacing: 2,
        color: b.watermark,
      }}
    >
      {b.watermarkText}
    </div>
  );
};
