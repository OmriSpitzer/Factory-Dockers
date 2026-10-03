export type Worker = {
    id: string;
    type: "assembler" | "tester" | "packager" | "shipper";
    status: "idle" | "working";
    progress: number;
    timeout?: number;
    image: string;
};