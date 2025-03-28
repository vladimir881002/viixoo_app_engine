import {
  Button,
  ButtonGroup,
  DialogActionTrigger,
  Select,
  createListCollection,
  Portal,
  Box,
  Input,
} from "@chakra-ui/react"
import useCustomToast from "../../hooks/useCustomToast"
import { useState, useRef } from "react"
import { type SubmitHandler, useForm } from "react-hook-form"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { type ApiError, WorkOrdersService } from "../../client"
import { handleError } from "../../utils"

import type { WorkOrderPublic, AddComponentsWorkOrder } from "../../client/types.gen"
import {
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTitle,
  DialogTrigger,
} from "../ui/dialog"
import { Field } from "../ui/field"


interface WorkOrderProps {
  item: WorkOrderPublic
}

export const blockRules = (isRequired = true) => {
  const rules: any = {}

  if (isRequired) {
    rules.required = "Campo obligatorio"
  }

  return rules
}

export const AddComponentsWorkOrders = ({ item }: WorkOrderProps) => {
  const {
      handleSubmit,
      reset,
      register,
      formState: { isValid, isSubmitting },
    } = useForm<AddComponentsWorkOrder>({
      mode: "onBlur",
      criteriaMode: "all",
    })
  const [isOpen, setIsOpen] = useState(false)
  function getProductsQueryOptions() {
    return {
      queryFn: () =>
        WorkOrdersService.readProducts(),
      queryKey: ["products"],
    }
  }
  const { data } = useQuery({
    ...getProductsQueryOptions(),
    placeholderData: (prevData) => prevData,
  })
  const items_data_products = data?.data ?? []
  const products = createListCollection({items:items_data_products})
  const contentRef = useRef<HTMLDivElement>(null)

  const { showSuccessToast } = useCustomToast()
  const queryClient = useQueryClient()
  const mutation = useMutation({
      mutationFn: (data: AddComponentsWorkOrder) =>
        WorkOrdersService.addComponentWorkorder({ requestBody: data }),
      onSuccess: () => {
        showSuccessToast("Componente agregado satisfactoriamente.")
        queryClient.invalidateQueries({ queryKey: ["workorders"] })
        reset()
      },
      onError: (err: ApiError) => {
        handleError(err)
      },
    })

    const onSubmit: SubmitHandler<AddComponentsWorkOrder> = async (data) => {
      mutation.mutate(data)
    }
  return (
    <DialogRoot
      size={{ base: "xs", md: "md" }}
      placement="center"
      open={isOpen}
      onOpenChange={({ open }) => setIsOpen(open)}
    >
      <DialogTrigger asChild>
      <Button maxH="35px" width="100%" variant="subtle" size="md" colorPalette="gray" >Agregar componente</Button>
      </DialogTrigger>
      <Portal>
      <DialogContent ref={contentRef}>
        <Box as="form" onSubmit={handleSubmit(onSubmit)}>
          <DialogHeader>
            <DialogTitle>Agregar componente</DialogTitle>
          </DialogHeader>
          <DialogBody>
           <Field label="Producto:">
          <Select.Root required collection={products} size="sm" {...register("product_id", blockRules())}>
            <Select.HiddenSelect />
            <Select.Control>
                  <Select.Trigger>
                    <Select.ValueText placeholder="Seleccione el producto" />
                  </Select.Trigger>
                  <Select.IndicatorGroup>
                    <Select.Indicator />
                  </Select.IndicatorGroup>
                </Select.Control>
              <Portal container={contentRef}>
                  <Select.Positioner>
                    <Select.Content>
                      {products.items.map((item) => (
                        <Select.Item item={item} key={item.value}>
                          {item.label}
                        </Select.Item>
                      ))}
                    </Select.Content>
                  </Select.Positioner>
                </Portal>
              </Select.Root>
              </Field>
              <Field label="Cantidad:">
              <Input type="number" {...register("quantity", {
                    required: "Ingrese una cantidad",
                    min: { value: 1, message: "La cantidad debe ser mayor a cero" },
                  })}/>
              </Field>
              <Input value={item.workorder_id} display='none' {...register("workorder_id")}
                  />
          </DialogBody>

          <DialogFooter gap={2}>
            <ButtonGroup>
              <DialogActionTrigger asChild>
                <Button
                  colorPalette="blue"
                  type="submit"
                  loading={isSubmitting}
                  disabled={!isValid}
                >
                  Agregar
                </Button>
              </DialogActionTrigger>
              <DialogActionTrigger asChild>
                <Button
                  variant="subtle"
                  colorPalette="gray"
                >
                  Cerrar
                </Button>
              </DialogActionTrigger>
            </ButtonGroup>
          </DialogFooter>
        </Box>
        <DialogCloseTrigger />
      </DialogContent>
      </Portal>
    </DialogRoot>
  )
}
