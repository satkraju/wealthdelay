import { createContext, useContext } from "react";
import { getBrand, type Brand, type BrandName } from "./theme";

// Active brand for a render. SceneVideo provides it from props.theme; defaults to
// LOR so any component that reads it outside a provider behaves as before.
export const BrandContext = createContext<Brand>(getBrand("lor"));

export const BrandProvider: React.FC<{ name?: BrandName; children: React.ReactNode }> = ({
  name,
  children,
}) => <BrandContext.Provider value={getBrand(name)}>{children}</BrandContext.Provider>;

export const useBrand = (): Brand => useContext(BrandContext);
