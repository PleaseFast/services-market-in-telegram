import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { register as registerApi } from "../api";

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8, "Min 8 characters"),
  role: z.enum(["specialist", "customer"]),
});

type FormValues = z.infer<typeof schema>;

export function RegisterPage() {
  const nav = useNavigate();
  const [err, setErr] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { role: "customer" },
  });
  const role = watch("role");

  async function onSubmit(values: FormValues) {
    setErr(null);
    try {
      const me = await registerApi(values.email, values.password, values.role);
      nav(me.role === "customer" ? "/c" : "/s/profile");
    } catch (e: unknown) {
      setErr((e as Error).message);
    }
  }

  return (
    <div className="max-w-md mx-auto pt-8">
      <Card>
        <CardHeader>
          <CardTitle>Create your account</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="space-y-1">
              <Label>I am a…</Label>
              <div className="grid grid-cols-2 gap-2">
                {(["customer", "specialist"] as const).map((r) => (
                  <Button
                    type="button"
                    key={r}
                    variant={role === r ? "default" : "outline"}
                    onClick={() => setValue("role", r)}
                  >
                    {r === "customer" ? "Customer" : "Specialist"}
                  </Button>
                ))}
              </div>
              <input type="hidden" {...register("role")} />
            </div>
            <div className="space-y-1">
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" {...register("email")} />
              {errors.email && <p className="text-xs text-destructive">{errors.email.message}</p>}
            </div>
            <div className="space-y-1">
              <Label htmlFor="password">Password</Label>
              <Input id="password" type="password" {...register("password")} />
              {errors.password && <p className="text-xs text-destructive">{errors.password.message}</p>}
            </div>
            {err && <p className="text-sm text-destructive">{err}</p>}
            <Button type="submit" disabled={isSubmitting} className="w-full">
              {isSubmitting ? "Creating…" : "Create account"}
            </Button>
            <p className="text-sm text-muted-foreground text-center">
              Already have one? <Link to="/login" className="text-primary underline-offset-4 hover:underline">Sign in</Link>
            </p>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
